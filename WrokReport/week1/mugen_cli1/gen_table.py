import json
import os

x86_file_path="./x86"
riscv_file_path="./risc-v"

def isfailed(logpath):
    logfile=open(logpath,"r+")
    log=logfile.read()
    logfile.close()
    if "LOG_ERROR" in log:
        return True
    return False

log_dir=riscv_file_path+"/logs"
log_fail_dir=riscv_file_path+"/logs_failed"
x86_log_dir=x86_file_path+"/logs"
x86_log_faile_dir=x86_file_path+"/logs_failed"

lists_file=open(riscv_file_path+"/lists/list_test","r")
lists=lists_file.read()
lists_file.close()
lists=lists.split("\n")
# print(lists)
table=open("table.md","w+")
head='''| 测试套/软件包名 | 测试用例名 | 状态 | 日志文件 | 原因 |\n| :-------------: | :--------: | :--: | :------: | :--: |\n'''
table.write(head)
for perlist in lists:
    suite_json=open(f"{riscv_file_path}/suite2cases/{perlist}.json","r")
    suite=suite_json.read()
    suite_json.close()
    # print(suite)
    suite=json.loads(suite)
    # print(suite["cases"])
    suitename=perlist
    for case in suite["cases"]:
        fail_suite_list=os.listdir(log_fail_dir)
        x86_fail_suite_list=os.listdir(x86_log_faile_dir)
        casename=case['name']
        status="success"
        if perlist in fail_suite_list:
            fail_case_list=os.listdir(log_fail_dir+f"/{perlist}")
            if casename in fail_case_list:
                status="fail"
                if perlist in x86_fail_suite_list:
                    x86_fail_case_list=os.listdir(x86_log_faile_dir+f"/{perlist}")
                    if casename in x86_fail_case_list:
                        status="x86 fail"

        suite_log_dir=log_dir+f"/{perlist}"
        if casename not in os.listdir(suite_log_dir):
            continue
        this_log_dir=log_dir+f"/{perlist}/{casename}"
        log_file=os.listdir(this_log_dir)[0]
        payload=f'| {suitename} | {casename} | {status} | {this_log_dir+"/"+log_file} | None |\n'
        suitename=""
        table.write(payload)