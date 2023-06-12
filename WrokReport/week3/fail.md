# fail排查

## OpenIPMI

### oe_test_service_ipmi

找不到内核模块

```bash
[root@openeuler-riscv64 ~]# modprobe ipmi_devintf
modprobe: FATAL: Module ipmi_devintf not found in directory /lib/modules/6.1.8-3.oe2303.riscv64
```

导致服务启动失败

## amanda

### oe_test_amanda_amcheck

``/usr/lib64/amanda/amanda-sh-lib.sh: line 40: /usr/bin/gettext: No such file or directory``

`` yum install gettext``装上gettext再测试即可通过测试。

## ant

### oe_test_ant_002

grep错误，grep加上选项``-P``之后参数以"\S"开头会造成grep错误：

```bash
[root@openeuler-riscv64 ant]# echo "1" | grep -P "\S"
grep: 程序错误
Aborted（核心已转储）
[root@openeuler-riscv64 ant]# echo "1" | grep -P "\Sasdf"
grep: 程序错误
Aborted（核心已转储）
```

## apache-commons-daemon 

### oe_test_jsvc_base

没有做riscv的适配，只有arm和x86的包：

```python
function pre_test() {
  LOG_INFO "Start environmental preparation."
  DNF_INSTALL "apache-commons-daemon tar"
  mkdir tmp && cd tmp
  if test "$(uname -i)"X == "x86_64"X; then
    echo 'get x86 architecture apache-commons-daemon pkg'
    cp ../common/x86/apache-commons-daemon.tar.gz ./
    tar -xvf apache-commons-daemon.tar.gz
  else
    echo 'get arm architecture apache-commons-daemon pkg'
    cp ../common/arm/apache-commons-daemon.zip ./
    unzip apache-commons-daemon.zip
  fi
  cd apache-commons-daemon
  current_path=$(
    cd "$(dirname $0)" || exit 1
    pwd
  )
  tar -xvf *.tar.gz
  LOG_INFO "End of environmental preparation!"
}
```

common目录中也只有arm和x86的包。

## arptables

### oe_test_service_arptables

单独测试时的报错和统一测试时的报错不一样，为找不到内核模块

```bash
[root@openeuler-riscv64 mugen]# arptables
modprobe: FATAL: Module arp_tables not found in directory /lib/modules/6.1.8-3.oe2303.riscv64
arptables v0.0.5: can't initialize arptables table `filter': arptables who? (do you need to insmod?)
Perhaps arptables or your kernel needs to be upgraded.
```

## AT

### oe_test_service

risc-v架构的openeuler没有默认安装initscripts，导致默认没有service命令

```service: command not found```

###  oe_test_rpm_suffix_name 

部分dnf源中的包的后缀（Release字段）为oe2而不是oe2303。不过看上去都像是测试用的包。

```bash
[root@openeuler-riscv64 mugen]# dnf list |grep -wv oe2303 | grep -v 'Packages\|Last metadata expiration check'
helloworld.riscv64                                      1.0-1.oe2                                         oetestsuite
helloworld-debuginfo.riscv64                            1.0-1.oe2                                         oetestsuite
helloworld-debugsource.riscv64                          1.0-1.oe2                                         oetestsuite
oetestsuite.noarch                                      0.1-2.oe2                                         oetestsuite
```

###  oe_test_OVS 

pre_test阶段执行```systemctl start openvswitch```失败，原因为找不到内核模块：

```bash
6月 08 16:35:37 openeuler-riscv64 ovs-ctl[2343]: Inserting openvswitch module
6月 08 16:35:37 openeuler-riscv64 ovs-ctl[2350]: modprobe: FATAL: Module openvswitch not found in directory /lib/modules/6.1.8-3.oe2303.riscv64
6月 08 16:35:37 openeuler-riscv64 ovs-ctl[2343]: [FAILED]
6月 08 16:35:37 openeuler-riscv64 systemd[1]: ovs-vswitchd.service: Control process exited, code=exited, status=1/FAILURE
```

之后在测试阶段执行命令```ovs-vsctl add-br br0```时会直接卡住直到超时。

### oe_test_docker_*

获取docker镜像的网址不存在：https://repo.openeuler.org/openEuler-23.03/docker_img/riscv64/openEuler-docker.riscv64.tar.xz

网址https://repo.openeuler.org/openEuler-23.03/docker_img只有[x86_64/](https://repo.openeuler.org/openEuler-23.03/docker_img/x86_64/)和[aarch64/](https://repo.openeuler.org/openEuler-23.03/docker_img/aarch64/)两个路径。

### oe_test_iSula_*

同oe_test_docker_*，获取镜像的网址不存在。

### oe_test_CPUinfo_001

risc-v架构的openeuler的```lscpu```命令输出格式和x86_64架构的不太一样，risc-v：

```bash
[root@openeuler-riscv64 ~]# lscpu
架构：            riscv64
  字节序：        Little Endian
CPU:              8
  在线 CPU 列表： 0-7
```

X86_64:

```bash
[root@localhost ~]# lscpu
Architecture:            x86_64
  CPU op-mode(s):        32-bit, 64-bit
  Address sizes:         40 bits physical, 48 bits virtual
  Byte Order:            Little Endian
CPU(s):                  8
  On-line CPU(s) list:   0-7
Vendor ID:               AuthenticAMD
  BIOS Vendor ID:        QEMU
  Model name:            QEMU Virtual CPU version 2.5+
    BIOS Model name:     pc-i440fx-8.0
    CPU family:          15
    Model:               107
    Thread(s) per core:  1
    Core(s) per socket:  8
    Socket(s):           1
    Stepping:            1
    BogoMIPS:            2000.02
    Flags:               fpu de pse tsc msr pae mce cx8 apic sep mtrr pge mca cm
                         ov pat pse36 clflush mmx fxsr sse sse2 ht syscall nx lm
                          rep_good nopl cpuid extd_apicid pni cx16 hypervisor la
                         hf_lm cmp_legacy svm 3dnowprefetch vmmcall
Virtualization features:
  Virtualization:        AMD-V
Caches (sum of all):
  L1d:                   512 KiB (8 instances)
  L1i:                   512 KiB (8 instances)
  L2:                    4 MiB (8 instances)
  L3:                    128 MiB (8 instances)
NUMA:
  NUMA node(s):          1
  NUMA node0 CPU(s):     0-7
Vulnerabilities:
  Itlb multihit:         Not affected
  L1tf:                  Not affected
  Mds:                   Not affected
  Meltdown:              Not affected
  Mmio stale data:       Not affected
  Retbleed:              Not affected
  Spec store bypass:     Not affected
  Spectre v1:            Mitigation; usercopy/swapgs barriers and __user pointer
                          sanitization
  Spectre v2:            Mitigation; Retpolines, STIBP disabled, RSB filling, PB
                         RSB-eIBRS Not affected
  Srbds:                 Not affected
  Tsx async abort:       Not affected
```

这两种架构下```lshw ```命令的输出格式也不一样，以产看cpu为例，risc-v:

```bash
[root@openeuler-riscv64 ~]# lshw -c cpu
  *-cpu:0
       description: CPU
       product: cpu
       physical id: 0
       bus info: cpu@0
       width: 32 bits
  *-cpu:1
       description: CPU
       product: cpu
       physical id: 1
       bus info: cpu@1
       width: 32 bits
  *-cpu:2
       description: CPU
       product: cpu
       physical id: 2
       bus info: cpu@2
       width: 32 bits
  *-cpu:3
       description: CPU
       product: cpu
       physical id: 3
       bus info: cpu@3
       width: 32 bits
  *-cpu:4
       description: CPU
       product: cpu
       physical id: 4
       bus info: cpu@4
       width: 32 bits
  *-cpu:5
       description: CPU
       product: cpu
       physical id: 5
       bus info: cpu@5
       width: 32 bits
  *-cpu:6
       description: CPU
       product: cpu
       physical id: 6
       bus info: cpu@6
       width: 32 bits
  *-cpu:7
       description: CPU
       product: cpu
       physical id: 7
       bus info: cpu@7
       width: 32 bits
  *-cpu:8 DISABLED
       description: CPU
       product: cpu-map
       physical id: 8
       bus info: cpu@8
```

X86_64:

```bash
[root@localhost ~]# lshw -c cpu
  *-cpu
       description: CPU
       product: QEMU Virtual CPU version 2.5+
       vendor: Advanced Micro Devices [AMD]
       physical id: 400
       bus info: cpu@0
       version: pc-i440fx-8.0
       slot: CPU 0
       size: 2GHz
       capacity: 2GHz
       width: 64 bits
       capabilities: fpu fpu_exception wp de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ht syscall nx x86-64 rep_good nopl cpuid extd_apicid pl
       configuration: cores=8 enabledcores=8 threads=1
```

所以测试脚本里的命令并不适用risc-v架构下的openeuler

### oe_test_criu

dnf源中没有软件包criu：

```bash
[root@openeuler-riscv64 ~]# dnf install criu
Last metadata expiration check: 0:35:09 ago on 2023年06月08日 星期四 16时44分14秒.
No match for argument: criu
Error: Unable to find a match: criu
```

### oe_test_iscsi

缺少内核模块configfs

```bash
[root@openeuler-riscv64 oe_test_iscsi]# targetcli
Could not load module: configfs
```

### oe_test_log_001

没有/var/log/messages这个文件

### oe_test_MEMinfo_001

x86_64和risc-v两种架构下```lshw -c memory ```命令的输出格式不一样，x86_64:

```bash
[root@localhost ~]# lshw -c memory
  *-firmware
       description: BIOS
       vendor: SeaBIOS
       physical id: 0
       version: rel-1.16.2-0-gea1b7a073390-prebuilt.qemu.org
       date: 04/01/2014
       size: 96KiB
  *-memory
       description: System Memory
       physical id: 1000
       size: 8GiB
       capabilities: ecc
       configuration: errordetection=multi-bit-ecc
     *-bank
          description: DIMM RAM
          vendor: QEMU
          physical id: 0
          slot: DIMM 0
          size: 8GiB
```

risc-v:

```bash
[root@openeuler-riscv64 oe_test_iscsi]# lshw -c memory
  *-memory
       description: System memory
       physical id: 9
       size: 3938MiB
```

测试机脚本中查找的字段在risc-v中没有。

### oe_test_numactl

没有NUMA支持

```bash
[root@openeuler-riscv64 oe_test_iscsi]# numactl -s
physcpubind: 0 1 2 3 4 5 6 7
No NUMA support available on this system.
```

### oe_test_perf

perf报错

```bash
[root@openeuler-riscv64 oe_test_iscsi]# timeout -k 15 1 perf record
Error:
cycles: PMU Hardware doesn't support sampling/overflow-interrupts. Try 'perf stat'
```

### oe_test_pwd_001

测试用例要执行命令```cd /etc/kernel```，但是risc-v下的openeuler并没有目录/etc/kernel

###  oe_test_skopeo 

执行```skopeo inspect --tls-verify=false docker://docker.io/nginx```时会报错提示目标镜像镜像没有riscv架构：

```bash
FATA[0003] Error parsing manifest for image: choosing image instance: no image found in manifest list for architecture riscv64, variant "", OS linux
```

或者直接程序崩溃，原因不明，报错在日志里。

### oe_test_syslog_logrotate_001

没有/var/log/messages和/var/log/messages-*.gz文件。

### **oe_test_yumgroup_001**

应该是oerv的yum源没有group data：

```bash
[root@openeuler-riscv64 oe_test_iscsi]# yum grouplist
Last metadata expiration check: 0:03:03 ago on 2023年06月09日 星期五 15时00分46秒.
Error: No group data available for configured repositories.
```

### oe_test_rollback

oerv预装git，不需要用yum装，所以命令```yum history list```查找不到git的安装记录，自然也无法回滚git的安装。

###  oe_test_arping 

配置文件里没填写NIC，在NIC中填上网卡名称再次测试即可成功通过。
