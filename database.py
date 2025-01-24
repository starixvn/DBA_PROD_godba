import time
from getpass import getpass
import pyodbc
import shutil
from datetime import datetime
import Applog
import re

# step 1: backup databases
def backup_a_database(dbserver, SQLlogin, pwd, database_name, destination_path):
    print(f"step 1: backup to '{destination_path}' ...")
    conn = pyodbc.connect(
        f"Driver={{SQL Server}};Server={dbserver};Database=master;uid={SQLlogin};pwd={pwd}", autocommit=True)
    cursor = conn.cursor()
    cursor.execute("select @@trancount")
    if cursor.fetchval() == 1:
        cursor.execute("commit")
    sqlcmd = fr"BACKUP DATABASE {database_name} TO  DISK = N'{destination_path}' WITH INIT, COPY_ONLY, COMPRESSION"
    # https://dba.stackexchange.com/questions/274122/python-script-leaves-the-database-in-restoring-mode
    cursor.execute(sqlcmd)
    while cursor.nextset():
        time.sleep(1)
    cursor.close()
    conn.close()


# step 2: copy to DR

# step 3: restore & config log shipping
def restore_a_database(dbserver, SQLlogin, pwd, database_name, source_path):
    print("step 3: restore database ...")
    conn = pyodbc.connect(
        f"Driver={{SQL Server}};Server={dbserver};Database=master;uid={SQLlogin};pwd={pwd}", autocommit=True)
    cursor = conn.cursor()
    # cursor.execute("commit")
    cursor.execute("select @@trancount")
    if cursor.fetchval() == 1:
        cursor.execute("commit")
    sqlcmd = fr"restore database {database_name} FROM  DISK = N'{source_path}' with norecovery"
    cursor.execute(sqlcmd)
    while cursor.nextset():
        time.sleep(1)
    cursor.close()
    conn.close()


def config_logshipping_primary(primaryserver, username, pwd, database_name, secondaryserver, backuppath):
    print("Step 4: config log shipping primary ....")
    with open("config_primary.sql", mode="r") as cnf_p_f:
        scr_config_primary = cnf_p_f.read()
    scr_config_primary = scr_config_primary.replace("@@@_database_name_@@@", database_name)
    scr_config_primary = scr_config_primary.replace("@@@_primary_database_@@@", database_name)
    scr_config_primary = scr_config_primary.replace("@@@_secondary_database_@@@", database_name)
    scr_config_primary = scr_config_primary.replace("@@@_secondary_server_@@@", secondaryserver)
    scr_config_primary = scr_config_primary.replace("@@@_backup_directory_@@@", fr"{backuppath}")
    scr_config_primary = scr_config_primary.replace("@@@_backup_share_@@@", fr"{backuppath}")
    scr_config_primary = scr_config_primary.replace("@@@_backup_job_name_@@@", f"LSBackup_{database_name}")
    scr_config_primary = scr_config_primary.replace("@@@_schedule_name_@@@", f"LSBackupSchedule_{primaryserver}1")

    conn = pyodbc.connect(
        f"Driver={{SQL Server}};Server={primaryserver};Database=msdb;uid={username};pwd={pwd}", autocommit=True)
    cursor = conn.cursor()
    cursor.execute("select @@trancount")
    if cursor.fetchval() == 1:
        cursor.execute("commit")
    cursor.execute(scr_config_primary)
    while cursor.nextset():
        pass
    cursor.close()
    conn.close()


def config_logshipping_primary_add(primaryserver, username, pwd, database_name, secondaryserver, backuppath):
    print("Step 4: config log shipping primary add....")
    with open("config_primary_add.sql", mode="r") as cnf_p_f:
        scr_config_primary = cnf_p_f.read()
    scr_config_primary = scr_config_primary.replace("@@@_database_name_@@@", database_name)
    scr_config_primary = scr_config_primary.replace("@@@_primary_database_@@@", database_name)
    scr_config_primary = scr_config_primary.replace("@@@_secondary_database_@@@", database_name)
    scr_config_primary = scr_config_primary.replace("@@@_secondary_server_@@@", secondaryserver)
    scr_config_primary = scr_config_primary.replace("@@@_backup_directory_@@@", fr"{backuppath}")
    scr_config_primary = scr_config_primary.replace("@@@_backup_share_@@@", fr"{backuppath}")
    scr_config_primary = scr_config_primary.replace("@@@_backup_job_name_@@@", f"LSBackup_{database_name}")
    scr_config_primary = scr_config_primary.replace("@@@_schedule_name_@@@", f"LSBackupSchedule_{primaryserver}1")

    conn = pyodbc.connect(
        f"Driver={{SQL Server}};Server={primaryserver};Database=msdb;uid={username};pwd={pwd}", autocommit=True)
    cursor = conn.cursor()
    cursor.execute("select @@trancount")
    if cursor.fetchval() == 1:
        cursor.execute("commit")
    cursor.execute(scr_config_primary)
    while cursor.nextset():
        pass
    cursor.close()
    conn.close()

def config_logshipping_secondary(secondaryserver, username, pwd, database_name, primaryserver, backuppath, copypath ):
    print("Step 5: config log shipping secondary ...")
    with open("config_secondary.sql", mode="r") as cnf_p_f:
        scr_config_secondary = cnf_p_f.read()

    scr_config_secondary = scr_config_secondary.replace("@@@_primary_server_@@@", primaryserver)
    scr_config_secondary = scr_config_secondary.replace("@@@_primary_database_@@@", database_name)
    scr_config_secondary = scr_config_secondary.replace("@@@_backup_source_directory_@@@", fr"{backuppath}")
    scr_config_secondary = scr_config_secondary.replace("@@@_backup_destination_directory_@@@", fr"{copypath}")
    scr_config_secondary = scr_config_secondary.replace("@@@_copy_job_name_@@@", f"LSCopy_{primaryserver}_{database_name}")
    scr_config_secondary = scr_config_secondary.replace("@@@_restore_job_name_@@@", f"LSRestore_{primaryserver}_{database_name}")
    scr_config_secondary = scr_config_secondary.replace("@@@_secondary_database_@@@", database_name)

    conn = pyodbc.connect(
        f"Driver={{SQL Server}};Server={secondaryserver};Database=msdb;uid={username};pwd={pwd}", autocommit=True)
    cursor = conn.cursor()
    # cursor.execute("commit")
    cursor.execute("select @@trancount")
    if cursor.fetchval() == 1:
        cursor.execute("commit")
    cursor.execute(scr_config_secondary)
    while cursor.nextset():
        time.sleep(1)
    cursor.close()
    conn.close()



def config_logshipping_check_backupjob(dbserver, SQLlogin, pwd, databasename):
    try:
        conn = pyodbc.connect(
            f"Driver={{SQL Server}};Server={dbserver};Database=msdb;uid={SQLlogin};pwd={pwd}",
            autocommit=True)
        cursor = conn.cursor()
        cursor.execute("select top 1 1 from msdb.dbo.log_shipping_primary_databases where primary_database = ?", databasename)
        if cursor.fetchval() == 1:
            result = 1
        else:
            result = 0
        cursor.close()
        conn.close()
    except Exception as e:
        Applog.write_log(str(e))
        result = -1
        cursor.close()
        conn.close()
    return result

def server_get_databases(dbserver, SQLlogin, pwd):
    if SQLlogin == "" or pwd == "":
        return []
    try:
        connection = pyodbc.connect(
            f"Driver={{SQL Server}};Server={dbserver};Database=master;uid={SQLlogin};pwd={pwd}",
            autocommit=True)
        cursor = connection.cursor()
        cursor.execute("select @@trancount")
        if cursor.fetchval() == 1:
            cursor.execute("commit")
        sqlcmd = fr"select name from sys.databases"
        cursor.execute(sqlcmd)
        qresult = cursor.fetchall()
        ds = [item[0] for item in qresult]
        cursor.close()
        return ds
    except Exception as e:
        Applog.write_log(str(e))


def check_username_pwd(dbserver, SQLlogin, pwd, dbname='master'):
    result = -1
    try:
        conn = pyodbc.connect(
            f"Driver={{SQL Server}};Server={dbserver};Database={dbname};uid={SQLlogin};pwd={pwd}",
            autocommit=True)
        cursor = conn.cursor()
        cursor.execute("select name from sys.login_token where name = 'sysadmin'")
        if cursor.fetchval() == 'sysadmin':
            result = 1
        cursor.close()
        conn.close()
    except Exception as e:
        Applog.write_log(str(e))
        result = -1
        cursor.close()
        conn.close()
    return result

def get_obj_definition(dbserver, sqllogin, pwd, dbname, objname):
    try:
        conn = pyodbc.connect(
            f"Driver={{SQL Server}};Server={dbserver};Database={dbname};uid={sqllogin};pwd={pwd}",
            autocommit=True)
        cursor = conn.cursor()
        cursor.execute("select definition from sys.sql_modules where object_id = object_id(?)", objname)
        qResult = cursor.fetchone()
        if qResult:
            return qResult[0]
        else:
            return None
    except Exception as e:
        Applog.write_log(str(e))
    return None



def check_existingobject(dbserver, SQLlogin, pwd, objname, dbname='master'):
    try:
        conn = pyodbc.connect(
            f"Driver={{SQL Server}};Server={dbserver};Database={dbname};uid={SQLlogin};pwd={pwd}",
            autocommit=True)
        cursor = conn.cursor()
        cursor.execute("select count(1) from sys.sql_modules where object_id = object_id(?)", objname)
        result = cursor.fetchone()
    except Exception as e:
        Applog.write_log(str(e))
    return result[0] > 0


def check_objecttype(dbserver, SQLlogin, pwd, objname, dbname='master'):
    try:
        conn = pyodbc.connect(
            f"Driver={{SQL Server}};Server={dbserver};Database={dbname};uid={SQLlogin};pwd={pwd}",
            autocommit=True)
        cursor = conn.cursor()
        cursor.execute("select type from sys.objects where name = ?", objname)
        result = cursor.fetchone()
        return result[0].strip()
    except Exception as e:
        Applog.write_log(str(e))
        return None


def execute_a_query(dbserver, sqllogin, pwd, dbname, querytext,trustedConnection=0):
    try:
        if trustedConnection ==1:
            conn = pyodbc.connect(
                f"Driver={{SQL Server}};Server={dbserver};Database={dbname};Trusted_Connection=yes;",
                autocommit=True)
        else:
            conn = pyodbc.connect(
                f"Driver={{SQL Server}};Server={dbserver};Database={dbname};uid={sqllogin};pwd={pwd}",
                autocommit=True)
        cursor = conn.cursor()
        cursor.execute(querytext)
        
        result =[]
        result.append(cursor.fetchall())
        
        while cursor.nextset():
            result.append(cursor.fetchall())
        cursor.close()
        conn.close()    
        return result
    except Exception as e:
        Applog.write_log(str(e))

def set_obj_definition(dbserver, sqllogin, pwd, dbname, objdefinition):
    execute_a_query(dbserver, sqllogin, pwd, dbname, objdefinition)

def get_obj_permission(dbserver, sqllogin, pwd, dbname, objname):
    try:
        conn = pyodbc.connect(
            f"Driver={{SQL Server}};Server={dbserver};Database={dbname};uid={sqllogin};pwd={pwd}",
            autocommit=True)
        cursor = conn.cursor()
        cursor.execute("select  string_agg( 'GRANT ' + permission_name + ' ON ' + o.name + ' TO ' + u.name collate SQL_Latin1_General_CP1_CI_AS + ';',char(10) ) as objpermission \
                        from sys.database_permissions p \
                            inner join sys.database_principals u on p.grantee_principal_id = u.principal_id \
                            inner join sys.objects o on p.major_id = o.object_id \
                        where o.name = ?", objname)
        qResult = cursor.fetchone()
        if qResult:
            return qResult[0]
        else:
            return None
    except Exception as e:
        Applog.write_log(str(e))
    return None


def set_obj_permission(dbserver, sqllogin, pwd, dbname, objpermission):
    execute_a_query(dbserver, sqllogin, pwd, dbname, objpermission)


def create_or_alter_obj(objectdefinition, objecttype):
    if objecttype.strip() == 'P':
        objectdefinition = re.sub(r'\bCREATE([ \t]+)(PROCEDURE)\b',
                              lambda match: 'ALTER' + match.group(1) + match.group(2),
                              objectdefinition, flags=re.IGNORECASE)
        objectdefinition = re.sub(r'\bCREATE([ \t]+)(PROC)\b',
                              lambda match: 'ALTER' + match.group(1) + match.group(2),
                              objectdefinition, flags=re.IGNORECASE)
    elif objecttype in ('FN', 'IF', 'TF'):
        objectdefinition = re.sub(r'\bCREATE([ \t]+)(FUNCTION)\b',
                              lambda match: 'ALTER' + match.group(1) + match.group(2),
                              objectdefinition, flags=re.IGNORECASE)
    return objectdefinition

def sync_SPList_to_destination(sourceserver, sourcelogin, sourcepwd, sourcedb, destserver, destlogin, destpwd, destdb, SPList, action):
    failedcnt = 0
    try:
        for SP in SPList:
            SP = SP.strip()
            if SP == '':
                continue
            if action in ('schema', 'both'):
                objdefiniton = get_obj_definition(sourceserver, sourcelogin, sourcepwd, sourcedb, SP)
                if objdefiniton is not None:
                    objtype = check_objecttype(sourceserver, sourcelogin, sourcepwd, SP, sourcedb)
                    if check_existingobject(destserver, destlogin, destpwd, SP, destdb):
                        objdefiniton = create_or_alter_obj(objdefiniton, objtype)
                    set_obj_definition(destserver, destlogin, destpwd, destdb, objdefiniton)
                else:
                    failedcnt += 1
                    print(f"{SP} does not exists at source")
                    continue
            if action in ('permission', 'both'):
                objpermission = get_obj_permission(sourceserver, sourcelogin, sourcepwd, sourcedb, SP)
                if objpermission is not None:
                    set_obj_permission(destserver, destlogin, destpwd, destdb, objpermission)
            print(f"{SP} was sync")
    except Exception as e:
        failedcnt += 1
        print(f"error found at {SP}", e)
        Applog.write_log(str(e))

    return failedcnt
