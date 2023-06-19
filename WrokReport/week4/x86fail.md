# x86 fail排查

## alsa-utils

### oe_test_service_alsa-restore

测试之前没有安装pciutils，所以没有lspci工具，直接没过下面这个判断：

```bash
    if ! lspci | grep -i audio; then
        LOG_INFO "The environment does not support testing"
        exit 1
```

由于启动时没有添加音频设备，所以安装pciutils之后依然会报错。

在高于7.0版本的qemu中使用``` -audiodev pa,id=snd0 -device usb-audio,audiodev=snd0 ```参数添加音频设备，会出现以下报错```qemu-system-riscv64: -audiodev pa,id=snd0: Parameter 'driver' does not accept value 'pa'```。

在低于7.0版本的qemu中使用参数```-device intel-hda -device hda-duplex```可以成功添加音频设备，此时在x86中测试成功，在risc-v中测试失败：用命令lspci可以找到音频设别，但是用命令aplay -l显示没有声卡。

##  anaconda

###  oe_test_service_zram

没有启用zram

```bash
can't read /usr/libexec/anaconda/zramswapon: No such file or directory
Failed to start zram.service: Unit zram.service not found.
```

## aspell

### oe_test_aspell_01

1. x86的openeuler上没有预装unzip，所以pre_test()中的```unzip common/aspell6-en-2020.12.07-0.zip```指令执行失败。
2. 现在执行命令```echo aaa | aspell -a```之后输出的词汇有31个，所以开头变成了```& aaa 31 0:```，而不是```& aaa 15 0:```，所以命令```echo aaa | aspell -a | grep "& aaa 15 0:"```执行失败

## AT

###  oe_test_dmesg_messages_log

oerv在dmesg中有不少报错信息：

```bash
[    0.801329] syscon-poweroff: probe of poweroff failed with error -16
[    0.804027] riscv-pmu-sbi: Perf sampling/filtering is not supported as sscof extension is not available
[ 9280.523477] systemd[1]: systemd-journald.service: Failed with result 'watchdog'.
[10242.592051] systemd[1]: systemd-journald.service: Failed with result 'watchdog'.
[11225.529926] systemd[1]: systemd-journald.service: Failed with result 'watchdog'.
[12193.559976] systemd[1]: systemd-journald.service: Failed with result 'watchdog'.
[13237.422999] systemd[1]: systemd-journald.service: Failed with result 'watchdog'.
[14314.496504] systemd[1]: systemd-journald.service: Failed with result 'watchdog'.
[15421.609070] systemd[1]: systemd-journald.service: Failed with result 'watchdog'.
[16324.471698] systemd[1]: systemd-journald.service: Failed with result 'watchdog'.
[17345.464831] systemd[1]: systemd-journald.service: Failed with result 'watchdog'.
[18296.481135] systemd[1]: systemd-journald.service: Failed with result 'watchdog'.
[19361.581037] systemd[1]: systemd-journald.service: Failed with result 'watchdog'.
[20333.402876] systemd[1]: systemd-journald.service: Failed with result 'watchdog'.
[21315.396326] systemd[1]: systemd-journald.service: Failed with result 'watchdog'.
[22908.392342] systemd[1]: systemd-journald.service: Failed with result 'watchdog'.
[23904.481955] systemd[1]: systemd-journald.service: Failed with result 'watchdog'.
[26773.576304] systemd[1]: systemd-journald.service: Failed with result 'watchdog'.
[27717.333955] systemd[1]: systemd-journald.service: Failed with result 'watchdog'.
[28747.405090] systemd[1]: systemd-journald.service: Failed with result 'watchdog'.
[29802.411159] systemd[1]: systemd-journald.service: Failed with result 'watchdog'.
[30762.401223] systemd[1]: systemd-journald.service: Failed with result 'watchdog'.
[32709.421065] systemd[1]: systemd-journald.service: Failed with result 'watchdog'.
[32709.529001] systemd[1]: dnf-makecache.service: Main process exited, code=exited, status=1/FAILURE
[32709.534805] systemd[1]: dnf-makecache.service: Failed with result 'exit-code'.
[32709.548195] systemd[1]: Failed to start dnf makecache.
[33789.389317] systemd[1]: systemd-journald.service: Failed with result 'watchdog'.
[34695.360003] systemd[1]: systemd-journald.service: Failed with result 'watchdog'.
[35674.364424] systemd[1]: systemd-journald.service: Failed with result 'watchdog'.
[36697.409252] systemd[1]: systemd-journald.service: Failed with result 'watchdog'.
[38589.531631] systemd[1]: systemd-journald.service: Failed with result 'watchdog'.
[39571.353585] systemd[1]: systemd-journald.service: Failed with result 'watchdog'.
[41609.313755] systemd[1]: systemd-journald.service: Failed with result 'watchdog'.
[46376.437773] systemd[1]: systemd-journald.service: Failed with result 'watchdog'.
```

oerv没有/var/log/messages这个文件：

```bash
grep: /var/log/messages: No such file or directory
```

x86下/var/log/messages文件中有不少报错信息：

```bash
May 26 02:06:09 localhost kernel: [    1.752638] jitterentropy: Initialization failed with host not compliant with requirements: 2
May 26 02:06:09 localhost rngd[253]: [rdrand]: Initialization Failed
May 26 02:06:14 localhost rngd[253]: [jitter]: Initialization Failed
May 26 02:06:14 localhost rngd[253]: [pkcs11]: Initialization Failed
May 26 02:06:24 localhost systemd-tmpfiles[1021]: /usr/lib/tmpfiles.d/systemd.conf:19: Failed to resolve user 'systemd-network': No such process
May 26 02:06:24 localhost systemd-tmpfiles[1021]: /usr/lib/tmpfiles.d/systemd.conf:20: Failed to resolve user 'systemd-network': No such process
May 26 02:06:24 localhost systemd-tmpfiles[1021]: /usr/lib/tmpfiles.d/systemd.conf:21: Failed to resolve user 'systemd-network': No such process
May 26 02:06:24 localhost systemd-tmpfiles[1021]: /usr/lib/tmpfiles.d/systemd.conf:22: Failed to resolve user 'systemd-network': No such process
May 26 02:06:45 localhost kernel: [   52.117456] Error: Driver 'pcspkr' is already registered, aborting...
May 26 02:06:53 localhost kdumpctl[1594]: Starting kdump: [FAILED]
May 26 02:06:53 localhost systemd[1]: kdump.service: Main process exited, code=exited, status=1/FAILURE
May 26 02:06:53 localhost systemd[1]: kdump.service: Failed with result 'exit-code'.
May 26 02:06:53 localhost systemd[1]: Failed to start Crash recovery kernel arming.
May 26 02:06:54 localhost kernel: [   60.914046] powernow_k8: Power state transitions not supported
May 26 02:06:54 localhost kernel: [   60.923272] powernow_k8: Power state transitions not supported
May 26 02:06:54 localhost kernel: [   60.932507] powernow_k8: Power state transitions not supported
May 26 02:06:54 localhost kernel: [   60.944536] powernow_k8: Power state transitions not supported
May 26 02:06:54 localhost kernel: [   60.946294] powernow_k8: Power state transitions not supported
May 26 02:06:54 localhost kernel: [   60.953691] powernow_k8: Power state transitions not supported
May 26 02:06:54 localhost kernel: [   60.959211] powernow_k8: Power state transitions not supported
May 26 02:06:54 localhost kernel: [   60.959245] powernow_k8: Power state transitions not supported
May 26 02:11:15 localhost [RPM][5001]: install perl-Error-1:0.17029-3.oe2303.noarch: success
May 26 02:11:18 localhost [RPM][5001]: install perl-Error-1:0.17029-3.oe2303.noarch: success
May 26 03:10:49 localhost dnf[5582]: Failed determining last makecache time.
May 26 03:50:39 localhost kernel: [    1.777871] jitterentropy: Initialization failed with host not compliant with requirements: 2
May 26 03:50:39 localhost rngd[254]: [rdrand]: Initialization Failed
May 26 03:50:44 localhost rngd[254]: [jitter]: Initialization Failed
May 26 03:50:44 localhost rngd[254]: [pkcs11]: Initialization Failed
May 26 03:50:54 localhost systemd-tmpfiles[1031]: /usr/lib/tmpfiles.d/systemd.conf:19: Failed to resolve user 'systemd-network': No such process
May 26 03:50:54 localhost systemd-tmpfiles[1031]: /usr/lib/tmpfiles.d/systemd.conf:20: Failed to resolve user 'systemd-network': No such process
May 26 03:50:54 localhost systemd-tmpfiles[1031]: /usr/lib/tmpfiles.d/systemd.conf:21: Failed to resolve user 'systemd-network': No such process
May 26 03:50:54 localhost systemd-tmpfiles[1031]: /usr/lib/tmpfiles.d/systemd.conf:22: Failed to resolve user 'systemd-network': No such process
May 26 03:51:02 localhost dracut-pre-pivot[1212]: ln: failed to create symbolic link '/sysroot/boot/initramfs-6.1.19-7.0.0.17.oe2303.x86_64.img': File exists
```

###  oe_test_firewalld 

测试前没有安装firewalld，安装之后x86测试通过，riscv执行```ip6tables -t nat -L```出错：

```bash
[root@openeuler-riscv64 mugen]# ip6tables -t nat -L
ip6tables v1.8.9 (legacy): can't initialize ip6tables table `nat': Table does not exist (do you need to insmod?)
Perhaps ip6tables or your kernel needs to be upgraded.
```

排查发现没有ip6table_nat.ko模块：

```bash
[root@openeuler-riscv64 mugen]# ls /lib/modules/`uname -r`/kernel/net/ipv6/netfilter/
ip6table_filter.ko  ip6_tables.ko       ip6t_REJECT.ko     nf_reject_ipv6.ko  nft_fib_ipv6.ko    nft_reject_ipv6.ko
ip6table_mangle.ko  ip6t_ipv6header.ko  nf_defrag_ipv6.ko  nf_socket_ipv6.ko  nf_tproxy_ipv6.ko
[root@openeuler-riscv64 mugen]# ls /lib/modules/`uname -r`/kernel/net/ipv4/netfilter/
iptable_filter.ko  iptable_nat.ko  iptable_security.ko  ipt_REJECT.ko    nf_defrag_ipv4.ko  nf_reject_ipv4.ko  nft_fib_ipv4.ko    nft_reject_ipv4.ko
iptable_mangle.ko  iptable_raw.ko  ip_tables.ko         ipt_SYNPROXY.ko  nf_dup_ipv4.ko     nf_socket_ipv4.ko  nf_tproxy_ipv4.ko
```

### oe_test_partition

没有swap分区和home分区

###  oe_test_docker_custom_image 

没有测试脚本：

```bash
Can't find the test script:oe_test_docker_custom_image, Please confirm whether the code is submitted.
```

### oe_test_cat_001

当前版本的openEuler（6.1.19-7.0.0.17.oe2303.x86_64和6.1.8-3.oe2303.riscv64）root用户的User ID Info是Super User而不是root，所以/etc/passwd中root的信息为```root:x:0:0:Super User:/root:/bin/bash```而不是```root:x:0:0:root:/root:/bin/bash```，导致grep失败

### oe_test_network_001

配置文件中没有填NIC（网卡名称），并且oerv中默认没有安装ethtool

##  audit 

x86中没有安装audit，riscv中没有安装initscripts和audit

##  atune

###  oe_test_service_atuned*

启动/usr/bin/atuned时报错：

riscv: 

```bash
fatal error: runtime: no plugin module data
```

x86:

```bash
ERRO[0000] cmd.Run() analysis failed with: exit status 1  file="pyservice.go:76"
```
