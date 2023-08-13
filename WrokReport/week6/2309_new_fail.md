# mugen 测试 2309 新增 fail

## 重新测试通过

+ ``libstoragemgmt/oe_test_service_libstoragemgmt``
+ ``netcf/oe_test_service_netcf-transaction``
+ ``smoke-basic-os/oe_test_cmp``
+ ``dbus/oe_test_socket_dbus``
+ ``libosinfo/oe_test_osinfo-install-script``
+ ``quota/oe_test_service_rpc-rquotad``
+ ``quota/oe_test_service_quota_nld``

## 软件包版本升级导致 grep 失败

+ ```smoke-basic-os/oe_test_aide_init_database```中```aide --init```预期输出应该包括"AIDE initialized database at /var/lib/aide/aide.db.new.gz"但是实际输出为：

```bash
Start timestamp: 2023-08-13 19:32:26 +0800 (AIDE 0.18.5)
AIDE successfully initialized database.
New AIDE database written to /var/lib/aide/aide.db.new.gz

Number of entries:	51176

---------------------------------------------------
The attributes of the (uncompressed) database(s):
---------------------------------------------------

/var/lib/aide/aide.db.new.gz
.......
```

+ ```smoke-basic-os/oe_test_rsyslog_10```中date命令的输出按空格分割第六个字符按预期为应为时区，例如```Sun Aug 13 07:34:01 PM CST 2023```但是实际输出为```Sun Aug 13 07:34:01 CST 2023```，输出按空格分割第六个字符变成了年份。

  

## 软件包依赖问题

+ ```gdm/oe_test_service_gdm```中缺少gcr4(riscv-64) 、libgcr-4.so.0.0.0()(64bit)、pipewire-gstreamer(riscv-64)
+ ```smoke-basic-os/oe_test_ima_v2_manual_gen_digest_01```中缺少libcrypto.so.1.1()(64bit)、libcrypto.so.1.1(OPENSSL_1_1_0)(64bit)
+ ```openscap/oe_test_ensure_security_compliance```中缺少openscap-scanner >= 1.2.5并找不到openscap软件包
+ ```smoke-basic-os/oe_test_ipv6_dnsmasq```中找不到bind-utils软件包
+ ```smoke-basic-os/oe_test_skopeo```中找不到skopeo软件包

* ```valgrind/oe_test_valgrind```中找不到valgrind软件包和glibc-debuginfo软件包

* ```tog-pegasus/oe_test_service_tog-pegasus```中找不到tog-pegasus软件包



## 镜像预装软件问题

* ```smoke-basic-os/oe_test_rsyslog_04```没有预装rsyslog

* ```smoke-basic-os/oe_test_iptables```没有预装iptables

* ```smoke-basic-os/oe_test_os-prober_01```没有预装os-prober

* ```smoke-basic-os/oe_test_glibc_getaddrinfo_01```缺少host命令

## 其他软件包问题

+ ```smoke-basic-os/oe_test_rpm_cmd```中运行命令```yum install```报错
+ ```smoke-basic-os/oe_test_user_debug_iotop_SCEN_01```中```iotop -b -n 1 -d 10```命令未能正确显示PRIO（显示为?sys）
+ ```smoke-basic-os/oe_test_sort```中新版sort命令默认不忽略空行，导致测试失败

## 其他问题

* ```libosinfo/oe_test_osinfo-db-import```中导出文件名按照当前时间命名，测试脚本中寻找的导出文件名是写死的。

* ```smoke-basic-os/oe_test_llvm```中clang调用ld报错

  命令为:

  ```bash
  "/usr/bin/ld" -pie --build-id --eh-frame-hdr -m elf64lriscv -X -dynamic-linker /lib/ld-linux-riscv64-lp64d.so.1 -o /tmp/test_llvm/test /lib/../lib64/Scrt1.o /lib/../lib64/crti.o crtbeginS.o -L/lib/../lib64 -L/usr/lib/../lib64 -L/lib64/lp64d -L/usr/lib64/lp64d -L/lib -L/usr/lib /tmp/llvm_test-032ffe.o -lgcc --as-needed -lgcc_s --no-as-needed -lc -lgcc --as-needed -lgcc_s --no-as-needed crtendS.o /lib/../lib64/crtn.o
  ```

  报错为:

  ```bash
  /usr/bin/ld: cannot find crtbeginS.o: No such file or directory
  /usr/bin/ld: cannot find -lgcc
  /usr/bin/ld: cannot find -lgcc_s
  ```
