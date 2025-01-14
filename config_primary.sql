
DECLARE @LS_BackupJobId	AS uniqueidentifier
DECLARE @LS_PrimaryId	AS uniqueidentifier
DECLARE @SP_Add_RetCode	As int


EXEC @SP_Add_RetCode = master.dbo.sp_add_log_shipping_primary_database
		@database = N'@@@_database_name_@@@'
		,@backup_directory = N'@@@_backup_directory_@@@'
		,@backup_share = N'@@@_backup_share_@@@'
		,@backup_job_name = N'@@@_backup_job_name_@@@'
		,@backup_retention_period = 4320
		,@backup_compression = 1
		,@backup_threshold = 60
		,@threshold_alert_enabled = 1
		,@history_retention_period = 5760
		,@backup_job_id = @LS_BackupJobId OUTPUT
		,@primary_id = @LS_PrimaryId OUTPUT
		,@overwrite = 1


IF (@@ERROR = 0 AND @SP_Add_RetCode = 0)
BEGIN

DECLARE @LS_BackUpScheduleUID	As uniqueidentifier
DECLARE @LS_BackUpScheduleID	AS int


EXEC msdb.dbo.sp_add_schedule
		@schedule_name =N'@@@_schedule_name_@@@'
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
		,@schedule_uid = @LS_BackUpScheduleUID OUTPUT
		,@schedule_id = @LS_BackUpScheduleID OUTPUT

EXEC msdb.dbo.sp_attach_schedule
		@job_id = @LS_BackupJobId
		,@schedule_id = @LS_BackUpScheduleID

EXEC msdb.dbo.sp_update_job
		@job_id = @LS_BackupJobId
		,@enabled = 1


END


EXEC master.dbo.sp_add_log_shipping_alert_job

EXEC master.dbo.sp_add_log_shipping_primary_secondary
		@primary_database = N'@@@_primary_database_@@@'
		,@secondary_server = N'@@@_secondary_server_@@@'
		,@secondary_database = N'@@@_secondary_database_@@@'
		,@overwrite = 1
