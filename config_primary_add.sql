

EXEC master.dbo.sp_add_log_shipping_primary_secondary
		@primary_database = N'@@@_primary_database_@@@'
		,@secondary_server = N'@@@_secondary_server_@@@'
		,@secondary_database = N'@@@_secondary_database_@@@'
		,@overwrite = 1
