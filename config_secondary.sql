
DECLARE @LS_Secondary__CopyJobId	AS uniqueidentifier
DECLARE @LS_Secondary__RestoreJobId	AS uniqueidentifier
DECLARE @LS_Secondary__SecondaryId	AS uniqueidentifier
DECLARE @LS_Add_RetCode	As int


EXEC @LS_Add_RetCode = master.dbo.sp_add_log_shipping_secondary_primary
		@primary_server = N'@@@_primary_server_@@@'
		,@primary_database = N'@@@_primary_database_@@@'
		,@backup_source_directory = N'@@@_backup_source_directory_@@@'
		,@backup_destination_directory = N'@@@_backup_destination_directory_@@@'
		,@copy_job_name = N'@@@_copy_job_name_@@@'
		,@restore_job_name = N'@@@_restore_job_name_@@@'
		,@file_retention_period = 4320
		,@overwrite = 1
		,@copy_job_id = @LS_Secondary__CopyJobId OUTPUT
		,@restore_job_id = @LS_Secondary__RestoreJobId OUTPUT
		,@secondary_id = @LS_Secondary__SecondaryId OUTPUT

IF (@@ERROR = 0 AND @LS_Add_RetCode = 0)
BEGIN

DECLARE @LS_SecondaryCopyJobScheduleUID	As uniqueidentifier
DECLARE @LS_SecondaryCopyJobScheduleID	AS int


EXEC msdb.dbo.sp_add_schedule
		@schedule_name =N'DefaultCopyJobSchedule'
		,@enabled = 1
		,@freq_type = 4
		,@freq_interval = 1
		,@freq_subday_type = 4
		,@freq_subday_interval = 15
		,@freq_recurrence_factor = 0
		,@active_start_date = 20240517
		,@active_end_date = 99991231
		,@active_start_time = 0
		,@active_end_time = 235900
		,@schedule_uid = @LS_SecondaryCopyJobScheduleUID OUTPUT
		,@schedule_id = @LS_SecondaryCopyJobScheduleID OUTPUT

EXEC msdb.dbo.sp_attach_schedule
		@job_id = @LS_Secondary__CopyJobId
		,@schedule_id = @LS_SecondaryCopyJobScheduleID

DECLARE @LS_SecondaryRestoreJobScheduleUID	As uniqueidentifier
DECLARE @LS_SecondaryRestoreJobScheduleID	AS int


EXEC msdb.dbo.sp_add_schedule
		@schedule_name =N'DefaultRestoreJobSchedule'
		,@enabled = 1
		,@freq_type = 4
		,@freq_interval = 1
		,@freq_subday_type = 4
		,@freq_subday_interval = 15
		,@freq_recurrence_factor = 0
		,@active_start_date = 20240517
		,@active_end_date = 99991231
		,@active_start_time = 0
		,@active_end_time = 235900
		,@schedule_uid = @LS_SecondaryRestoreJobScheduleUID OUTPUT
		,@schedule_id = @LS_SecondaryRestoreJobScheduleID OUTPUT

EXEC msdb.dbo.sp_attach_schedule
		@job_id = @LS_Secondary__RestoreJobId
		,@schedule_id = @LS_SecondaryRestoreJobScheduleID


END


DECLARE @LS_Add_RetCode2	As int


IF (@@ERROR = 0 AND @LS_Add_RetCode = 0)
BEGIN

EXEC @LS_Add_RetCode2 = master.dbo.sp_add_log_shipping_secondary_database
		@secondary_database = N'@@@_secondary_database_@@@'
		,@primary_server = N'@@@_primary_server_@@@'
		,@primary_database = N'@@@_primary_database_@@@'
		,@restore_delay = 0
		,@restore_mode = 1
		,@disconnect_users	= 0
		,@restore_threshold = 45
		,@threshold_alert_enabled = 1
		,@history_retention_period	= 5760
		,@overwrite = 1

END


IF (@@error = 0 AND @LS_Add_RetCode = 0)
BEGIN

EXEC msdb.dbo.sp_update_job
		@job_id = @LS_Secondary__CopyJobId
		,@enabled = 1

EXEC msdb.dbo.sp_update_job
		@job_id = @LS_Secondary__RestoreJobId
		,@enabled = 1

END
