# RISC-V openEuler 上的LTP测试

### 一、宿主机内环境搭建

使用的操作系统为macos

1. 安装qemu，brew中有编译好的qemu 8.0.0

```bash
brew install qemu
```

2. 下载 openEuler RISC-V 系统镜像

下载[fw_payload_oe_uboot_2304.bin](https://mirror.iscas.ac.cn/openeuler-sig-riscv/openEuler-RISC-V/preview/openEuler-23.03-V1-riscv64/QEMU/fw_payload_oe_uboot_2304.bin)、[openEuler-23.03-V1-base-qemu-preview.qcow2.zst](https://mirror.iscas.ac.cn/openeuler-sig-riscv/openEuler-RISC-V/preview/openEuler-23.03-V1-riscv64/QEMU/openEuler-23.03-V1-base-qemu-preview.qcow2.zst)和[start_vm.sh](https://mirror.iscas.ac.cn/openeuler-sig-riscv/openEuler-RISC-V/preview/openEuler-23.03-V1-riscv64/QEMU/start_vm.sh)。

内核版本为：6.1.19-2.oe2303.riscv64

3. 准备两个测试用的虚拟盘

一个LTP称为LTP_DEV，用于一般的磁盘操作，要求容量>=300M；另一个为LTP_BIG_DEV，用于大容量I/O操作，要求>=500M。

```bash
qemu-img create -f qcow2 ext2g.qcow2 2G # 做LTP_BIG_DEV用
qemu-img create -f qcow2 ext1g.qcow2 1G # 做LTP_DEV用
```

4. 修改启动脚本

首先将```drive="$(ls *.qcow2)"```改为```drive="openEuler-23.03-V1-base-qemu-preview.qcow2"```。再为qemu启动参数添加上如下内容：

```bash
  -drive file=ext2g.qcow2,format=qcow2,id=hd1 \
  -drive file=ext1g.qcow2,format=qcow2,id=hd2 \
  -device virtio-blk-device,drive=hd1 \
  -device virtio-blk-device,drive=hd2 \
```

5. 用启动脚本启动openEuler RISC-V

```bash
chmod +x start_vm.sh
./start_vm.sh
```

### 二、openEuler内环境搭建

1. 将添加的虚拟盘格式化为ext4

```bash
fdisk /dev/vdb
mkfs.ext4 /dev/vdb1
fdisk /dev/vdc
mkfs.ext4 /dev/vdc1
```

2. 添加1G的swap分区

```bash
dd if=/dev/zero of=/swapfile bs=1M count=1000
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
```

3. 下载安装LTP

```bash
cd /
git clone https://github.com/linux-test-project/ltp.git
```

4. 编译安装LTP

先安装编译工具

```bash
dnf install gcc git make pkgconf autoconf automake bison flex m4 kernel-tools kernel-headers kernel-devel glibc-headers
```

再安装测试用工具

```bash
dnf install openssl-devel libacl-devel libaio-devel libcap-devel ethtool expect-devel xfsprogs-devel btrfs-progs quota nfs-utils genisoimage squashfs-tools ntfs-3g sysstat lksctp-tools-devel irqbalance
```

编译安装

```bash
cd /ltp
make autotools
./configure --with-bash --with-expect --with-perl --with-python
make
make install
```

### 三、运行测试及运行结果

1. 运行测试

首先下载[skipped.6.1.19.tests](https://gitee.com/laokz/oerv/blob/master/ltp/skipped.6.1.19.tests)，用来跳过不必要的测试。测试直接使用root用户。

```bash
mkdir -p /ltp/tmp
export LTP_TIMEOUT_MUL=10
cd /opt/ltp
./runltp -p -S /ltp/skipped.tests -o tests.output -d /ltp/tmp -b /dev/vdc1 -B ext4 -z /dev/vdb1 -Z ext4
```

> 运行了大概16小时

后面可能还需要单独测试。

```bash
./runltp -q -d /ltp/tmp -b /dev/vdc1 -B ext4 -z /dev/vdb1 -Z ext4 -f 测试套名 -s 测试tag名
```

2. 运行结果统计

按测试用例统计：

```
Total Tests: 2179

Total Skipped Tests: 289

Total Failures: 42
```

按测试功能点手工统计测试日志中的Summary：

```
总数：6190
passed：5890
failed：36
broken：3
skipped：242
warnings：19
```

3. 失败用例统计

```
clock_nanosleep02         
leapsec01                 
clock_settime03           
finit_module02            
getrusage04               
getxattr04                
ioctl_loop05              
msgstress04               
nanosleep01               
madvise06                 
poll02                    
prctl09                   
pselect01                 
pselect01_64              
select02                  
timer_settime03           
perf_event_open01         
vma05                     
memcg_subgroup_charge     
memcg_max_usage_in_bytes  
memcg_use_hierarchy       
memcg_usage_in_bytes      
df01_ext2_sh              
df01_ext3_sh              
df01_ext4_sh              
df01_xfs_sh               
df01_vfat_sh              
df01_exfat_sh             
df01_ntfs_sh              
mkfs01_sh                 
mkfs01_ext2_sh            
mkfs01_ext3_sh            
mkfs01_ext4_sh            
mkfs01_xfs_sh             
mkfs01_btrfs_sh           
mkfs01_minix_sh           
mkfs01_msdos_sh           
mkfs01_vfat_sh            
mkfs01_ntfs_sh            
mkswap01_sh               
cve-2018-12896            
tpci                   
```

其中clock_nanosleep02、nanosleep01、poll02、prctl09、pselect01、pselect01_64、select02、getrusage04单独测试的时候没有问题。查看日志发现这些测试一开始不通过的原因基本都为time相关。

### 四、失败用例详细数据

#### clock_nanosleep02

> 单独测试时没有问题

```
tst_test.c:1289: TINFO: Timeout per run is 0h 50m 00s
tst_timer_test.c:357: TINFO: CLOCK_MONOTONIC resolution 4000000ns
tst_timer_test.c:369: TINFO: prctl(PR_GET_TIMERSLACK) = 50us
tst_timer_test.c:263: TINFO: clock_nanosleep() sleeping for 1000us 500 iterations, threshold 8450.01us
tst_timer_test.c:305: TINFO: min 1692us, max 9241us, median 4486us, trunc mean 4363.33us (discarded 25)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: clock_nanosleep() sleeping for 2000us 500 iterations, threshold 8450.01us
tst_timer_test.c:305: TINFO: min 3171us, max 10628us, median 7013us, trunc mean 6853.55us (discarded 25)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: clock_nanosleep() sleeping for 5000us 300 iterations, threshold 8450.04us
tst_timer_test.c:305: TINFO: min 6102us, max 15324us, median 10205us, trunc mean 10214.35us (discarded 15)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: clock_nanosleep() sleeping for 10000us 100 iterations, threshold 8450.33us
tst_timer_test.c:305: TINFO: min 12110us, max 22335us, median 17590us, trunc mean 17355.88us (discarded 5)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: clock_nanosleep() sleeping for 25000us 50 iterations, threshold 8451.29us
tst_timer_test.c:305: TINFO: min 27471us, max 40642us, median 34621us, trunc mean 34113.85us (discarded 2)
tst_timer_test.c:314: TFAIL: clock_nanosleep() slept for too long

 Time: us | Frequency
--------------------------------------------------------------------------------
    27471 | ***********-
    28165 | **********************************
    28859 | *********************************************-
    29553 | ***********-
    30247 | *********************************************-
    30941 | 
    31635 | **********************+
    32329 | **********************+
    33023 | *********************************************-
    33717 | **********************+
    34411 | **********************************
    35105 | *********************************************-
    35799 | **********************************
    36493 | *********************************************-
    37187 | **********************+
    37881 | ********************************************************************
    38575 | 
    39269 | **********************************
    39963 | **********************+
--------------------------------------------------------------------------------
    694us | 1 sample = 11.33333 '*', 22.66667 '+', 45.33333 '-', non-zero '.'

tst_timer_test.c:263: TINFO: clock_nanosleep() sleeping for 100000us 10 iterations, threshold 8537.00us
tst_timer_test.c:305: TINFO: min 102234us, max 112622us, median 111251us, trunc mean 109024.11us (discarded 1)
tst_timer_test.c:314: TFAIL: clock_nanosleep() slept for too long

 Time: us | Frequency
--------------------------------------------------------------------------------
   102234 | **********************+
   102781 | **********************+
   103328 | 
   103875 | 
   104422 | 
   104969 | 
   105516 | 
   106063 | **********************+
   106610 | 
   107157 | 
   107704 | 
   108251 | 
   108798 | 
   109345 | 
   109892 | **********************+
   110439 | 
   110986 | **********************+
   111533 | *********************************************-
   112080 | ********************************************************************
--------------------------------------------------------------------------------
    547us | 1 sample = 22.66667 '*', 45.33333 '+', 90.66666 '-', non-zero '.'

tst_timer_test.c:263: TINFO: clock_nanosleep() sleeping for 1000000us 2 iterations, threshold 12400.00us
tst_timer_test.c:305: TINFO: min 1004959us, max 1010940us, median 1004959us, trunc mean 1004959.00us (discarded 1)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
```

#### leapsec01

```
tst_test.c:1289: TINFO: Timeout per run is 0h 50m 00s
leapsec01.c:130: TINFO: test start at 16:30:55.360810702
leapsec01.c:100: TINFO: now is     16:30:55.364796924
leapsec01.c:104: TINFO: sleep until 16:30:56.364796924
leapsec01.c:112: TINFO: now is     16:30:56.369236122
leapsec01.c:115: TINFO: hrtimer early expiration is not detected.
leapsec01.c:138: TINFO: scheduling leap second 08:00:00.000000000
leapsec01.c:144: TINFO: setting time to        07:59:58.000000000
leapsec01.c:88: TINFO: 07:59:58.4637091000 adjtimex: clock synchronized
leapsec01.c:88: TINFO: 07:59:58.006892000 adjtimex: clock synchronized
leapsec01.c:88: TINFO: 07:59:58.007291000 adjtimex: clock synchronized
leapsec01.c:88: TINFO: 07:59:58.007836000 adjtimex: clock synchronized
leapsec01.c:88: TINFO: 16:30:56.893487966000 adjtimex: clock synchronized
leapsec01.c:88: TINFO: 16:30:57.405716372000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:30:57.922065822000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:30:58.432682211000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:30:58.948552655000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:30:59.466543122000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:30:59.981677559000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:00.491683941000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:01.5170361000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:01.522010815000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:02.39031272000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:02.546707630000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:03.61049058000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:03.575945492000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:04.82347837000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:04.598274282000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:05.113189717000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:05.623220099000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:06.132247472000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:06.643719870000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:07.153914254000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:07.664187640000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:08.174548026000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:08.684016403000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:09.195962806000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:09.705184180000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:10.221276627000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:10.734919048000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:11.246807451000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:11.752548788000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:12.260737152000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:12.769718523000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:13.285113963000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:13.794743341000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:14.308666765000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:14.820586168000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:15.329066535000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:15.841891947000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:16.354924362000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:16.862884723000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:17.369616071000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:17.882898488000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:18.397429918000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:18.905554281000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:19.414292650000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:19.929339086000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:20.439072466000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:20.948116838000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:21.451587152000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:21.955878474000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:22.464357840000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:22.980114284000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:23.498581756000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:24.6926121000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:24.522040557000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:25.36283985000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:25.550907416000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:26.57415761000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:26.565660125000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:27.82587581000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:27.597610017000 adjtimex: insert leap second
leapsec01.c:88: TINFO: 16:31:28.112878455000 adjtimex: insert leap second
leapsec01.c:84: TBROK: adjtimex status 8208 not set
```

#### clock_settime03

```
tst_test.c:1289: TINFO: Timeout per run is 0h 50m 00s
clock_settime03.c:35: TINFO: Testing variant: syscall with old kernel spec
Test timeouted, sending SIGKILL!
tst_test.c:1335: TINFO: If you are running on slow machine, try exporting LTP_TIMEOUT_MUL > 1
tst_test.c:1337: TBROK: Test killed! (timeout?)
```

#### finit_module02

```
tst_test.c:1289: TINFO: Timeout per run is 0h 50m 00s
finit_module02.c:114: TPASS: TestName: invalid-fd: EBADF (9)
finit_module02.c:114: TPASS: TestName: zero-fd: EINVAL (22)
finit_module02.c:114: TPASS: TestName: null-param: EFAULT (14)
finit_module02.c:114: TPASS: TestName: invalid-param: EINVAL (22)
finit_module02.c:114: TPASS: TestName: invalid-flags: EINVAL (22)
tst_capability.c:29: TINFO: Dropping CAP_SYS_MODULE(16)
finit_module02.c:114: TPASS: TestName: no-perm: EPERM (1)
tst_capability.c:41: TINFO: Permitting CAP_SYS_MODULE(16)
finit_module02.c:114: TPASS: TestName: module-exists: EEXIST (17)
finit_module02.c:114: TFAIL: TestName: file-not-readable expected ETXTBSY: EBADF (9)
finit_module02.c:114: TPASS: TestName: directory: EINVAL (22)
```

#### getrusage04

> 单独测试时没有问题

```
getrusage04    0  TINFO  :  Expected timers granularity is 4000 us
getrusage04    0  TINFO  :  Using 1 as multiply factor for max [us]time increment (1000+4000us)!
getrusage04    0  TINFO  :  utime:        8259us; stime:       37169us
getrusage04    0  TINFO  :  utime:        8259us; stime:       41024us
getrusage04    0  TINFO  :  utime:        8259us; stime:       44780us
getrusage04    0  TINFO  :  utime:        9143us; stime:       54859us
getrusage04    1  TFAIL  :  getrusage04.c:132: stime increased > 5000us:
```
#### getxattr04
```
  tst_device.c:268: TINFO: Using test device LTP_DEV='/dev/vdc1'
tst_test.c:888: TINFO: Formatting /dev/vdc1 with xfs opts='' extra opts=''
tst_test.c:899: TBROK: mount(/dev/vdc1, mntpoint, xfs, 0, (nil)) failed: ENODEV (19)
```
#### ioctl_loop05
```
tst_test.c:1289: TINFO: Timeout per run is 0h 50m 00s
tst_device.c:88: TINFO: Found free device 0 '/dev/loop0'
tst_device.c:535: TWARN: stat(/dev/root) failed: ENOENT (2)
```
#### msgstress04
```
msgstress04    0  TINFO  :  Found 32000 available message queues
msgstress04    0  TINFO  :  Using upto 2097092 pids
Fork failure in the first child of child group 23441
Fork failure in the first child of child group 23436
Fork failure in the second child of child group 23420
Fork failure in the first child of child group 23421
Fork failure in the first child of child group 23395
Fork failure in the first child of child group 23434
Fork failure in the first child of child group 23427
Fork failure in the second child of child group 23447
Fork failure in the second child of child group 23424
Fork failure in the second child of child group 23448
Fork failure in the first child of child group 23443
Fork failure in the first child of child group 23399
Fork failure in the first child of child group 23450
Fork failure in the first child of child group 23398
Fork failure in the first child of child group 23440
Fork failure in the second child of child group 23416
Fork failure in the first child of child group 23425
Fork failure in the second child of child group 23445
Fork failure in the second child of child group 23439
Fork failure in the second child of child group 23414
Fork failure in the second child of child group 23413
Fork failure in the first child of child group 23686
Fork failure in the first child of child group 23678
Fork failure in the second child of child group 23688
Fork failure in the first child of child group 23698
Fork failure in the first child of child group 23699
Fork failure in the first child of child group 23681
Fork failure in the second child of child group 23684
Fork failure in the first child of child group 23679
Fork failure in the second child of child group 23676
Fork failure in the first child of child group 23697
Fork failure in the first child of child group 23703
Fork failure in the second child of child group 23690
Fork failure in the first child of child group 23687
Fork failure in the first child of child group 23680
Fork failure in the second child of child group 23696
Fork failure in the second child of child group 23693
Fork failure in the second child of child group 23826
Fork failure in the second child of child group 23819
Fork failure in the second child of child group 23830
Fork failure in the second child of child group 23832
Fork failure in the second child of child group 23835
Fork failure in the second child of child group 23851
msgstress04    1  TFAIL  :  msgstress04.c:204: Fork failed (may be OK if under stress)
Fork failure in the first child of child group 23844
Fork failure in the second child of child group 23847
Fork failure in the first child of child group 23845
```
#### nanosleep01

> 单独测试时没有问题

```
tst_test.c:1289: TINFO: Timeout per run is 0h 50m 00s
tst_timer_test.c:357: TINFO: CLOCK_MONOTONIC resolution 4000000ns
tst_timer_test.c:369: TINFO: prctl(PR_GET_TIMERSLACK) = 50us
tst_timer_test.c:263: TINFO: nanosleep() sleeping for 1000us 500 iterations, threshold 8450.01us
tst_timer_test.c:305: TINFO: min 1926us, max 8973us, median 4560us, trunc mean 4466.40us (discarded 25)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: nanosleep() sleeping for 2000us 500 iterations, threshold 8450.01us
tst_timer_test.c:305: TINFO: min 3168us, max 10489us, median 7152us, trunc mean 7004.58us (discarded 25)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: nanosleep() sleeping for 5000us 300 iterations, threshold 8450.04us
tst_timer_test.c:305: TINFO: min 6593us, max 15201us, median 10324us, trunc mean 10509.56us (discarded 15)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: nanosleep() sleeping for 10000us 100 iterations, threshold 8450.33us
tst_timer_test.c:305: TINFO: min 12536us, max 22820us, median 17234us, trunc mean 17139.72us (discarded 5)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: nanosleep() sleeping for 25000us 50 iterations, threshold 8451.29us
tst_timer_test.c:305: TINFO: min 26650us, max 39701us, median 35240us, trunc mean 34471.94us (discarded 2)
tst_timer_test.c:314: TFAIL: nanosleep() slept for too long

 Time: us | Frequency
--------------------------------------------------------------------------------
    26650 | *************+
    27337 | 
    28024 | ****************************************+
    28711 | *************+
    29398 | ***************************
    30085 | ***************************
    30772 | *************+
    31459 | ****************************************+
    32146 | ****************************************+
    32833 | *************+
    33520 | ****************************************+
    34207 | ***************************
    34894 | ******************************************************-
    35581 | ****************************************+
    36268 | ********************************************************************
    36955 | ******************************************************-
    37642 | ********************************************************************
    38329 | ******************************************************-
    39016 | ****************************************+
--------------------------------------------------------------------------------
    687us | 1 sample = 13.60000 '*', 27.20000 '+', 54.40000 '-', non-zero '.'

tst_timer_test.c:263: TINFO: nanosleep() sleeping for 100000us 10 iterations, threshold 8537.00us
tst_timer_test.c:305: TINFO: min 103434us, max 114590us, median 109901us, trunc mean 109453.33us (discarded 1)
tst_timer_test.c:314: TFAIL: nanosleep() slept for too long

 Time: us | Frequency
--------------------------------------------------------------------------------
   103434 | **********************************
   104022 | 
   104610 | **********************************
   105198 | 
   105786 | 
   106374 | 
   106962 | 
   107550 | **********************************
   108138 | 
   108726 | **********************************
   109314 | **********************************
   109902 | 
   110490 | **********************************
   111078 | 
   111666 | 
   112254 | ********************************************************************
   112842 | 
   113430 | 
   114018 | ********************************************************************
--------------------------------------------------------------------------------
    588us | 1 sample = 34.00000 '*', 68.00000 '+', 136.00000 '-', non-zero '.'

tst_timer_test.c:263: TINFO: nanosleep() sleeping for 1000000us 2 iterations, threshold 12400.00us
tst_timer_test.c:305: TINFO: min 1008977us, max 1014236us, median 1008977us, trunc mean 1008977.00us (discarded 1)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
```
#### madvise06
```
tst_test.c:1289: TINFO: Timeout per run is 0h 50m 00s
madvise06.c:106: TINFO: dropping caches
madvise06.c:81: TINFO: Initial meminfo, later values are relative to this (except memcg)
madvise06.c:82: TINFO: 	Swap: 524 Kb
madvise06.c:84: TINFO: 	SwapCached: 24 Kb
madvise06.c:86: TINFO: 	Cached: 40908 Kb
madvise06.c:88: TINFO: 	cgmem.usage_in_bytes: 256 Kb
madvise06.c:93: TINFO: 	cgmem.memsw.usage_in_bytes: 256 Kb
madvise06.c:97: TINFO: 	cgmem.kmem.usage_in_bytes: 16 Kb
madvise06.c:151: TINFO: mapping 409600 Kb (102400 pages), limit 204800 Kb, pass threshold 102400 Kb
madvise06.c:81: TINFO: Before mmap
madvise06.c:82: TINFO: 	Swap: 0 Kb
madvise06.c:84: TINFO: 	SwapCached: 0 Kb
madvise06.c:86: TINFO: 	Cached: 152 Kb
madvise06.c:88: TINFO: 	cgmem.usage_in_bytes: 256 Kb
madvise06.c:93: TINFO: 	cgmem.memsw.usage_in_bytes: 256 Kb
madvise06.c:97: TINFO: 	cgmem.kmem.usage_in_bytes: 24 Kb
madvise06.c:191: TINFO: PageFault(before mmap): 0
madvise06.c:81: TINFO: Before dirty
madvise06.c:82: TINFO: 	Swap: 0 Kb
madvise06.c:84: TINFO: 	SwapCached: 0 Kb
madvise06.c:86: TINFO: 	Cached: 152 Kb
madvise06.c:88: TINFO: 	cgmem.usage_in_bytes: 256 Kb
madvise06.c:93: TINFO: 	cgmem.memsw.usage_in_bytes: 256 Kb
madvise06.c:97: TINFO: 	cgmem.kmem.usage_in_bytes: 28 Kb
madvise06.c:196: TINFO: PageFault(before dirty): 0
madvise06.c:198: TINFO: PageFault(after dirty): 0
madvise06.c:81: TINFO: Before madvise
madvise06.c:82: TINFO: 	Swap: 207280 Kb
madvise06.c:84: TINFO: 	SwapCached: 376 Kb
madvise06.c:86: TINFO: 	Cached: 202628 Kb
madvise06.c:88: TINFO: 	cgmem.usage_in_bytes: 204636 Kb
madvise06.c:93: TINFO: 	cgmem.memsw.usage_in_bytes: 411384 Kb
madvise06.c:97: TINFO: 	cgmem.kmem.usage_in_bytes: 1764 Kb
madvise06.c:81: TINFO: After madvise
madvise06.c:82: TINFO: 	Swap: 305904 Kb
madvise06.c:84: TINFO: 	SwapCached: 99148 Kb
madvise06.c:86: TINFO: 	Cached: 103804 Kb
madvise06.c:88: TINFO: 	cgmem.usage_in_bytes: 204596 Kb
madvise06.c:93: TINFO: 	cgmem.memsw.usage_in_bytes: 411396 Kb
madvise06.c:97: TINFO: 	cgmem.kmem.usage_in_bytes: 1764 Kb
madvise06.c:219: TFAIL: less than 102400 Kb were moved to the swap cache
madvise06.c:229: TINFO: PageFault(madvice / no mem access): 1
madvise06.c:233: TINFO: PageFault(madvice / mem access): 3202
madvise06.c:81: TINFO: After page access
madvise06.c:82: TINFO: 	Swap: 207368 Kb
madvise06.c:84: TINFO: 	SwapCached: 616 Kb
madvise06.c:86: TINFO: 	Cached: 202464 Kb
madvise06.c:88: TINFO: 	cgmem.usage_in_bytes: 204712 Kb
madvise06.c:93: TINFO: 	cgmem.memsw.usage_in_bytes: 411388 Kb
madvise06.c:97: TINFO: 	cgmem.kmem.usage_in_bytes: 1764 Kb
madvise06.c:238: TFAIL: 3201 pages were faulted out of 2 max

HINT: You _MAY_ be missing kernel fixes, see:

https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=55231e5c898c
https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=8de15e920dc8
```
#### poll02

> 单独测试时没有问题

```
tst_test.c:1289: TINFO: Timeout per run is 0h 50m 00s
tst_timer_test.c:357: TINFO: CLOCK_MONOTONIC resolution 4000000ns
tst_timer_test.c:369: TINFO: prctl(PR_GET_TIMERSLACK) = 50us
tst_timer_test.c:263: TINFO: poll() sleeping for 1000us 500 iterations, threshold 8450.01us
tst_timer_test.c:305: TINFO: min 2115us, max 9244us, median 4745us, trunc mean 5028.47us (discarded 25)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: poll() sleeping for 2000us 500 iterations, threshold 8450.01us
tst_timer_test.c:305: TINFO: min 3035us, max 12400us, median 7198us, trunc mean 7045.77us (discarded 25)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: poll() sleeping for 5000us 300 iterations, threshold 8450.04us
tst_timer_test.c:305: TINFO: min 5925us, max 14947us, median 10582us, trunc mean 10712.45us (discarded 15)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: poll() sleeping for 10000us 100 iterations, threshold 8450.33us
tst_timer_test.c:305: TINFO: min 12390us, max 22475us, median 17698us, trunc mean 17241.29us (discarded 5)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: poll() sleeping for 25000us 50 iterations, threshold 8451.29us
tst_timer_test.c:305: TINFO: min 28937us, max 40719us, median 33948us, trunc mean 34322.06us (discarded 2)
tst_timer_test.c:314: TFAIL: poll() slept for too long

 Time: us | Frequency
--------------------------------------------------------------------------------
    28937 | *********************************************-
    29558 | **********************************
    30179 | *********************************************-
    30800 | ***********-
    31421 | ***********-
    32042 | **********************************
    32663 | *********************************************-
    33284 | *********************************************-
    33905 | ***********-
    34526 | **********************************
    35147 | **********************+
    35768 | *********************************************-
    36389 | **********************+
    37010 | **********************+
    37631 | **********************************
    38252 | ***********-
    38873 | **********************+
    39494 | 
    40115 | ********************************************************************
--------------------------------------------------------------------------------
    621us | 1 sample = 11.33333 '*', 22.66667 '+', 45.33333 '-', non-zero '.'

tst_timer_test.c:263: TINFO: poll() sleeping for 100000us 10 iterations, threshold 8537.00us
tst_timer_test.c:305: TINFO: min 103951us, max 112651us, median 109864us, trunc mean 109339.00us (discarded 1)
tst_timer_test.c:314: TFAIL: poll() slept for too long

 Time: us | Frequency
--------------------------------------------------------------------------------
   103951 | **********************************
   104409 | 
   104867 | 
   105325 | 
   105783 | 
   106241 | 
   106699 | **********************************
   107157 | 
   107615 | **********************************
   108073 | **********************************
   108531 | 
   108989 | 
   109447 | **********************************
   109905 | 
   110363 | 
   110821 | **********************************
   111279 | **********************************
   111737 | **********************************
   112195 | ********************************************************************
--------------------------------------------------------------------------------
    458us | 1 sample = 34.00000 '*', 68.00000 '+', 136.00000 '-', non-zero '.'

tst_timer_test.c:263: TINFO: poll() sleeping for 1000000us 2 iterations, threshold 12400.00us
tst_timer_test.c:305: TINFO: min 1010725us, max 1014508us, median 1010725us, trunc mean 1010725.00us (discarded 1)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
```
#### prctl09

> 单独测试时没有问题

```
tst_test.c:1289: TINFO: Timeout per run is 0h 50m 00s
tst_timer_test.c:357: TINFO: CLOCK_MONOTONIC resolution 4000000ns
tst_timer_test.c:369: TINFO: prctl(PR_GET_TIMERSLACK) = 200us
tst_timer_test.c:263: TINFO: prctl() sleeping for 1000us 500 iterations, threshold 8600.01us
tst_timer_test.c:305: TINFO: min 2195us, max 10648us, median 4641us, trunc mean 4765.16us (discarded 25)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: prctl() sleeping for 2000us 500 iterations, threshold 8600.01us
tst_timer_test.c:305: TINFO: min 3185us, max 11359us, median 7154us, trunc mean 7096.20us (discarded 25)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: prctl() sleeping for 5000us 300 iterations, threshold 8600.04us
tst_timer_test.c:305: TINFO: min 5844us, max 14744us, median 10568us, trunc mean 10506.71us (discarded 15)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: prctl() sleeping for 10000us 100 iterations, threshold 8600.33us
tst_timer_test.c:305: TINFO: min 12296us, max 22414us, median 17441us, trunc mean 17374.95us (discarded 5)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: prctl() sleeping for 25000us 50 iterations, threshold 8601.29us
tst_timer_test.c:305: TINFO: min 28515us, max 40447us, median 36728us, trunc mean 35302.58us (discarded 2)
tst_timer_test.c:314: TFAIL: prctl() slept for too long

 Time: us | Frequency
--------------------------------------------------------------------------------
    28515 | *************+
    29143 | ******+
    29771 | ******+
    30399 | ********************-
    31027 | ********************-
    31655 | 
    32283 | ********************-
    32911 | ******+
    33539 | ******+
    34167 | ******+
    34795 | ********************-
    35423 | *************+
    36051 | *************+
    36679 | ********************************************************************
    37307 | ******************************************************-
    37935 | *************+
    38563 | *************+
    39191 | ***************************
    39819 | 
    40447 | ******+
--------------------------------------------------------------------------------
    628us | 1 sample = 6.80000 '*', 13.60000 '+', 27.20000 '-', non-zero '.'

tst_timer_test.c:263: TINFO: prctl() sleeping for 100000us 10 iterations, threshold 8637.00us
tst_timer_test.c:305: TINFO: min 107203us, max 114490us, median 109808us, trunc mean 109919.33us (discarded 1)
tst_timer_test.c:314: TFAIL: prctl() slept for too long

 Time: us | Frequency
--------------------------------------------------------------------------------
   107203 | **********************************
   107587 | 
   107971 | **********************************
   108355 | **********************************
   108739 | 
   109123 | 
   109507 | ********************************************************************
   109891 | **********************************
   110275 | 
   110659 | **********************************
   111043 | **********************************
   111427 | 
   111811 | 
   112195 | 
   112579 | 
   112963 | 
   113347 | **********************************
   113731 | 
   114115 | **********************************
--------------------------------------------------------------------------------
    384us | 1 sample = 34.00000 '*', 68.00000 '+', 136.00000 '-', non-zero '.'

tst_timer_test.c:263: TINFO: prctl() sleeping for 1000000us 2 iterations, threshold 12400.00us
tst_timer_test.c:305: TINFO: min 1007217us, max 1015511us, median 1007217us, trunc mean 1007217.00us (discarded 1)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
```
#### pselect01

> 单独测试时没有问题

```
tst_test.c:1289: TINFO: Timeout per run is 0h 50m 00s
tst_timer_test.c:357: TINFO: CLOCK_MONOTONIC resolution 4000000ns
tst_timer_test.c:369: TINFO: prctl(PR_GET_TIMERSLACK) = 50us
tst_timer_test.c:263: TINFO: pselect() sleeping for 1000us 500 iterations, threshold 8450.01us
tst_timer_test.c:305: TINFO: min 1867us, max 9182us, median 4627us, trunc mean 4675.11us (discarded 25)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: pselect() sleeping for 2000us 500 iterations, threshold 8450.01us
tst_timer_test.c:305: TINFO: min 3145us, max 10705us, median 7370us, trunc mean 7186.89us (discarded 25)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: pselect() sleeping for 5000us 300 iterations, threshold 8450.04us
tst_timer_test.c:305: TINFO: min 6333us, max 15038us, median 10750us, trunc mean 10686.28us (discarded 15)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: pselect() sleeping for 10000us 100 iterations, threshold 8450.33us
tst_timer_test.c:305: TINFO: min 13009us, max 22429us, median 18152us, trunc mean 17787.95us (discarded 5)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: pselect() sleeping for 25000us 50 iterations, threshold 8451.29us
tst_timer_test.c:305: TINFO: min 28333us, max 38882us, median 35253us, trunc mean 34553.71us (discarded 2)
tst_timer_test.c:314: TFAIL: pselect() slept for too long

 Time: us | Frequency
--------------------------------------------------------------------------------
    28333 | ***********-
    28889 | 
    29445 | **********************+
    30001 | ***********-
    30557 | **********************+
    31113 | ***********-
    31669 | **********************************
    32225 | ***********-
    32781 | ********************************************************************
    33337 | **********************************
    33893 | 
    34449 | *********************************************-
    35005 | **********************************
    35561 | *********************************************-
    36117 | *********************************************-
    36673 | ********************************************************************
    37229 | **********************************
    37785 | **********************************
    38341 | **********************************
--------------------------------------------------------------------------------
    556us | 1 sample = 11.33333 '*', 22.66667 '+', 45.33333 '-', non-zero '.'

tst_timer_test.c:263: TINFO: pselect() sleeping for 100000us 10 iterations, threshold 8537.00us
tst_timer_test.c:305: TINFO: min 103388us, max 114957us, median 111835us, trunc mean 111052.89us (discarded 1)
tst_timer_test.c:314: TFAIL: pselect() slept for too long

 Time: us | Frequency
--------------------------------------------------------------------------------
   103388 | **********************+
   103997 | 
   104606 | 
   105215 | 
   105824 | 
   106433 | 
   107042 | 
   107651 | 
   108260 | 
   108869 | 
   109478 | 
   110087 | 
   110696 | *********************************************-
   111305 | ********************************************************************
   111914 | **********************+
   112523 | **********************+
   113132 | 
   113741 | **********************+
   114350 | **********************+
--------------------------------------------------------------------------------
    609us | 1 sample = 22.66667 '*', 45.33333 '+', 90.66666 '-', non-zero '.'

tst_timer_test.c:263: TINFO: pselect() sleeping for 1000000us 2 iterations, threshold 12400.00us
tst_timer_test.c:305: TINFO: min 1009830us, max 1011798us, median 1009830us, trunc mean 1009830.00us (discarded 1)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
```
#### pselect01_64

> 单独测试时没有问题

```
tst_test.c:1289: TINFO: Timeout per run is 0h 50m 00s
tst_timer_test.c:357: TINFO: CLOCK_MONOTONIC resolution 4000000ns
tst_timer_test.c:369: TINFO: prctl(PR_GET_TIMERSLACK) = 50us
tst_timer_test.c:263: TINFO: pselect() sleeping for 1000us 500 iterations, threshold 8450.01us
tst_timer_test.c:305: TINFO: min 2171us, max 9049us, median 4621us, trunc mean 4679.64us (discarded 25)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: pselect() sleeping for 2000us 500 iterations, threshold 8450.01us
tst_timer_test.c:305: TINFO: min 3192us, max 10400us, median 7236us, trunc mean 7122.09us (discarded 25)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: pselect() sleeping for 5000us 300 iterations, threshold 8450.04us
tst_timer_test.c:305: TINFO: min 6387us, max 14987us, median 10825us, trunc mean 10614.70us (discarded 15)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: pselect() sleeping for 10000us 100 iterations, threshold 8450.33us
tst_timer_test.c:305: TINFO: min 11626us, max 22406us, median 18021us, trunc mean 17430.51us (discarded 5)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: pselect() sleeping for 25000us 50 iterations, threshold 8451.29us
tst_timer_test.c:305: TINFO: min 28299us, max 40432us, median 34797us, trunc mean 34538.38us (discarded 2)
tst_timer_test.c:314: TFAIL: pselect() slept for too long

 Time: us | Frequency
--------------------------------------------------------------------------------
    28299 | ****************************************+
    28938 | 
    29577 | 
    30216 | ***************************
    30855 | ****************************************+
    31494 | *************+
    32133 | ****************************************+
    32772 | ********************************************************************
    33411 | ******************************************************-
    34050 | ****************************************+
    34689 | ********************************************************************
    35328 | ***************************
    35967 | ****************************************+
    36606 | ****************************************+
    37245 | ******************************************************-
    37884 | ********************************************************************
    38523 | *************+
    39162 | 
    39801 | ****************************************+
--------------------------------------------------------------------------------
    639us | 1 sample = 13.60000 '*', 27.20000 '+', 54.40000 '-', non-zero '.'

tst_timer_test.c:263: TINFO: pselect() sleeping for 100000us 10 iterations, threshold 8537.00us
tst_timer_test.c:305: TINFO: min 102615us, max 112796us, median 108952us, trunc mean 108524.78us (discarded 1)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: pselect() sleeping for 1000000us 2 iterations, threshold 12400.00us
tst_timer_test.c:305: TINFO: min 1010806us, max 1012114us, median 1010806us, trunc mean 1010806.00us (discarded 1)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
```
#### select02

> 单独测试时没有问题

```
tst_test.c:1289: TINFO: Timeout per run is 0h 50m 00s
select_var.h:109: TINFO: Testing libc select()
tst_timer_test.c:357: TINFO: CLOCK_MONOTONIC resolution 4000000ns
tst_timer_test.c:369: TINFO: prctl(PR_GET_TIMERSLACK) = 50us
tst_timer_test.c:263: TINFO: select() sleeping for 1000us 500 iterations, threshold 8450.01us
tst_timer_test.c:305: TINFO: min 1467us, max 9391us, median 4578us, trunc mean 4606.48us (discarded 25)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: select() sleeping for 2000us 500 iterations, threshold 8450.01us
tst_timer_test.c:305: TINFO: min 2537us, max 11173us, median 7235us, trunc mean 7115.21us (discarded 25)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: select() sleeping for 5000us 300 iterations, threshold 8450.04us
tst_timer_test.c:305: TINFO: min 6178us, max 15094us, median 11167us, trunc mean 10768.67us (discarded 15)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: select() sleeping for 10000us 100 iterations, threshold 8450.33us
tst_timer_test.c:305: TINFO: min 11346us, max 22767us, median 17209us, trunc mean 17187.93us (discarded 5)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: select() sleeping for 25000us 50 iterations, threshold 8451.29us
tst_timer_test.c:305: TINFO: min 28522us, max 40665us, median 35451us, trunc mean 34960.92us (discarded 2)
tst_timer_test.c:314: TFAIL: select() slept for too long

 Time: us | Frequency
--------------------------------------------------------------------------------
    28522 | *********+
    29162 | *******************-
    29802 | 
    30442 | *******************-
    31082 | 
    31722 | **************************************+
    32362 | *********+
    33002 | ********************************************************************
    33642 | *****************************
    34282 | **************************************+
    34922 | *********+
    35562 | ********************************************************************
    36202 | *******************-
    36842 | *******************-
    37482 | ************************************************+
    38122 | **************************************+
    38762 | *****************************
    39402 | *********+
    40042 | *********+
--------------------------------------------------------------------------------
    640us | 1 sample = 9.71429 '*', 19.42857 '+', 38.85714 '-', non-zero '.'

tst_timer_test.c:263: TINFO: select() sleeping for 100000us 10 iterations, threshold 8537.00us
tst_timer_test.c:305: TINFO: min 102359us, max 112756us, median 106330us, trunc mean 108049.11us (discarded 1)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: select() sleeping for 1000000us 2 iterations, threshold 12400.00us
tst_timer_test.c:305: TINFO: min 1005300us, max 1013766us, median 1005300us, trunc mean 1005300.00us (discarded 1)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_test.c:1289: TINFO: Timeout per run is 0h 50m 00s
select_var.h:112: TINFO: Testing SYS_select syscall
tst_timer_test.c:357: TINFO: CLOCK_MONOTONIC resolution 4000000ns
tst_timer_test.c:369: TINFO: prctl(PR_GET_TIMERSLACK) = 50us
tst_timer_test.c:263: TINFO: select() sleeping for 1000us 500 iterations, threshold 8450.01us
select_var.h:30: TCONF: syscall(-1) __NR_select not supported
tst_test.c:1289: TINFO: Timeout per run is 0h 50m 00s
select_var.h:115: TINFO: Testing SYS_pselect6 syscall
tst_timer_test.c:357: TINFO: CLOCK_MONOTONIC resolution 4000000ns
tst_timer_test.c:369: TINFO: prctl(PR_GET_TIMERSLACK) = 50us
tst_timer_test.c:263: TINFO: select() sleeping for 1000us 500 iterations, threshold 8450.01us
tst_timer_test.c:305: TINFO: min 2087us, max 9264us, median 4618us, trunc mean 4674.77us (discarded 25)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: select() sleeping for 2000us 500 iterations, threshold 8450.01us
tst_timer_test.c:305: TINFO: min 3144us, max 10541us, median 7252us, trunc mean 7187.78us (discarded 25)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: select() sleeping for 5000us 300 iterations, threshold 8450.04us
tst_timer_test.c:305: TINFO: min 6428us, max 15013us, median 10399us, trunc mean 10412.77us (discarded 15)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: select() sleeping for 10000us 100 iterations, threshold 8450.33us
tst_timer_test.c:305: TINFO: min 11793us, max 22475us, median 17349us, trunc mean 17134.75us (discarded 5)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_timer_test.c:263: TINFO: select() sleeping for 25000us 50 iterations, threshold 8451.29us
tst_timer_test.c:305: TINFO: min 29288us, max 40812us, median 35255us, trunc mean 35127.92us (discarded 2)
tst_timer_test.c:314: TFAIL: select() slept for too long

 Time: us | Frequency
--------------------------------------------------------------------------------
    29288 | ***************************
    29895 | ***************************
    30502 | *************+
    31109 | ******************************************************-
    31716 | ***************************
    32323 | ****************************************+
    32930 | ****************************************+
    33537 | *************+
    34144 | ***************************
    34751 | ********************************************************************
    35358 | ***************************
    35965 | ****************************************+
    36572 | ********************************************************************
    37179 | ***************************
    37786 | ***************************
    38393 | ******************************************************-
    39000 | ***************************
    39607 | *************+
    40214 | ******************************************************-
--------------------------------------------------------------------------------
    607us | 1 sample = 13.60000 '*', 27.20000 '+', 54.40000 '-', non-zero '.'

tst_timer_test.c:263: TINFO: select() sleeping for 100000us 10 iterations, threshold 8537.00us
tst_timer_test.c:305: TINFO: min 104642us, max 114669us, median 111853us, trunc mean 109843.67us (discarded 1)
tst_timer_test.c:314: TFAIL: select() slept for too long

 Time: us | Frequency
--------------------------------------------------------------------------------
   104642 | ********************************************************************
   105170 | 
   105698 | 
   106226 | 
   106754 | 
   107282 | 
   107810 | **********************************
   108338 | 
   108866 | **********************************
   109394 | 
   109922 | 
   110450 | 
   110978 | 
   111506 | ********************************************************************
   112034 | ********************************************************************
   112562 | 
   113090 | **********************************
   113618 | 
   114146 | **********************************
--------------------------------------------------------------------------------
    528us | 1 sample = 34.00000 '*', 68.00000 '+', 136.00000 '-', non-zero '.'

tst_timer_test.c:263: TINFO: select() sleeping for 1000000us 2 iterations, threshold 12400.00us
tst_timer_test.c:305: TINFO: min 1011803us, max 1014168us, median 1011803us, trunc mean 1011803.00us (discarded 1)
tst_timer_test.c:326: TPASS: Measured times are within thresholds
tst_test.c:1289: TINFO: Timeout per run is 0h 50m 00s
select_var.h:118: TINFO: Testing SYS_pselect6 time64 syscall
tst_timer_test.c:357: TINFO: CLOCK_MONOTONIC resolution 4000000ns
tst_timer_test.c:369: TINFO: prctl(PR_GET_TIMERSLACK) = 50us
tst_timer_test.c:263: TINFO: select() sleeping for 1000us 500 iterations, threshold 8450.01us
select_var.h:83: TCONF: __NR_pselect6 time64 variant not supported
tst_test.c:1289: TINFO: Timeout per run is 0h 50m 00s
select_var.h:121: TINFO: Testing SYS__newselect syscall
tst_timer_test.c:357: TINFO: CLOCK_MONOTONIC resolution 4000000ns
tst_timer_test.c:369: TINFO: prctl(PR_GET_TIMERSLACK) = 50us
tst_timer_test.c:263: TINFO: select() sleeping for 1000us 500 iterations, threshold 8450.01us
select_var.h:89: TCONF: syscall(-1) __NR__newselect not supported
```
#### timer_settime03
```
tst_kconfig.c:64: TINFO: Parsing kernel config '/proc/config.gz'
tst_test.c:1289: TINFO: Timeout per run is 0h 50m 00s
timer_settime03.c:105: TFAIL: Timer overrun counter is wrong: 767; expected 2147483647 or negative number

HINT: You _MAY_ be missing kernel fixes, see:

https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=78c9c4dfbf8c

HINT: You _MAY_ be vulnerable to CVE(s), see:

https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-12896
```
#### perf_event_open01
```
perf_event_open01    1  TFAIL  :  perf_event_open01.c:158: perf_event_open PERF_COUNT_HW_INSTRUCTIONS failed unexpectedly: TEST_ERRNO=EINVAL(22): Invalid argument
```
#### vma05
```
vma05 1 TINFO: timeout per run is 0h 50m 0s
vma05 1 TFAIL: [vdso] bug not patched
```
#### memcg_subgroup_charge
```
memcg_subgroup_charge 1 TINFO: timeout per run is 0h 50m 0s
memcg_subgroup_charge 1 TINFO: set /dev/memcg/memory.use_hierarchy to 0 failed
memcg_subgroup_charge 1 TINFO: Test that group and subgroup have no relationship
memcg_subgroup_charge 1 TINFO: Running memcg_process --mmap-anon -s 135168
memcg_subgroup_charge 1 TINFO: Warming up pid: 727902
memcg_subgroup_charge 1 TINFO: Process is still here after warm up: 727902
/opt/ltp/testcases/bin/memcg_lib.sh: line 170: 727902 Killed                  memcg_process "$@"
memcg_subgroup_charge 1 TFAIL: rss is 0, 135168 expected
/opt/ltp/testcases/bin/memcg_subgroup_charge.sh: line 38: echo: write error: No such process
memcg_subgroup_charge 1 TPASS: rss is 0 as expected
memcg_subgroup_charge 2 TINFO: Running memcg_process --mmap-anon -s 135168
memcg_subgroup_charge 2 TINFO: Warming up pid: 727922
memcg_subgroup_charge 2 TINFO: Process is still here after warm up: 727922
/opt/ltp/testcases/bin/memcg_lib.sh: line 170: 727922 Killed                  memcg_process "$@"
memcg_subgroup_charge 2 TFAIL: rss is 0, 135168 expected
/opt/ltp/testcases/bin/memcg_subgroup_charge.sh: line 38: echo: write error: No such process
memcg_subgroup_charge 2 TPASS: rss is 0 as expected
memcg_subgroup_charge 3 TINFO: Running memcg_process --mmap-anon -s 135168
memcg_subgroup_charge 3 TINFO: Warming up pid: 727942
memcg_subgroup_charge 3 TINFO: Process is still here after warm up: 727942
/opt/ltp/testcases/bin/memcg_lib.sh: line 170: 727942 Killed                  memcg_process "$@"
memcg_subgroup_charge 3 TFAIL: rss is 0, 135168 expected
/opt/ltp/testcases/bin/memcg_subgroup_charge.sh: line 38: echo: write error: No such process
memcg_subgroup_charge 3 TPASS: rss is 0 as expected
```
单独测试的时候出现了新的错误：

```
memcg_subgroup_charge 1 TINFO: timeout per run is 0h 50m 0s
memcg_subgroup_charge 1 TINFO: set /dev/memcg/memory.use_hierarchy to 0 failed
memcg_subgroup_charge 1 TINFO: Test that group and subgroup have no relationship
memcg_subgroup_charge 1 TINFO: Running memcg_process --mmap-anon -s 135168
memcg_subgroup_charge 1 TINFO: Warming up pid: 1721813
memcg_subgroup_charge 1 TINFO: Process is still here after warm up: 1721813
memcg_subgroup_charge 1 TBROK: timed out on memory.usage_in_bytes
/opt/ltp/testcases/bin/tst_test.sh: line 143: 1721813 Killed                  memcg_process "$@"  (wd: /dev/memcg/ltp_1721779)
```

#### memcg_max_usage_in_bytes

```
memcg_max_usage_in_bytes_test 1 TINFO: timeout per run is 0h 50m 0s
memcg_max_usage_in_bytes_test 1 TINFO: set /dev/memcg/memory.use_hierarchy to 0 failed
memcg_max_usage_in_bytes_test 1 TINFO: Test memory.max_usage_in_bytes
memcg_max_usage_in_bytes_test 1 TINFO: Running memcg_process --mmap-anon -s 4194304
memcg_max_usage_in_bytes_test 1 TINFO: Warming up pid: 727997
memcg_max_usage_in_bytes_test 1 TINFO: Process is still here after warm up: 727997
memcg_max_usage_in_bytes_test 1 TFAIL: memory.max_usage_in_bytes is 4456448, 4194304 expected
memcg_max_usage_in_bytes_test 2 TINFO: Test memory.memsw.max_usage_in_bytes
memcg_max_usage_in_bytes_test 2 TINFO: Running memcg_process --mmap-anon -s 4194304
memcg_max_usage_in_bytes_test 2 TINFO: Warming up pid: 728011
memcg_max_usage_in_bytes_test 2 TINFO: Process is still here after warm up: 728011
memcg_max_usage_in_bytes_test 2 TFAIL: memory.memsw.max_usage_in_bytes is 4456448, 4194304 expected
memcg_max_usage_in_bytes_test 3 TINFO: Test reset memory.max_usage_in_bytes
memcg_max_usage_in_bytes_test 3 TINFO: Running memcg_process --mmap-anon -s 4194304
memcg_max_usage_in_bytes_test 3 TINFO: Warming up pid: 728025
memcg_max_usage_in_bytes_test 3 TINFO: Process is still here after warm up: 728025
memcg_max_usage_in_bytes_test 3 TFAIL: memory.max_usage_in_bytes is 4456448, 4194304 expected
memcg_max_usage_in_bytes_test 3 TFAIL: memory.max_usage_in_bytes is 258048, 0 expected
memcg_max_usage_in_bytes_test 4 TINFO: Test reset memory.memsw.max_usage_in_bytes
memcg_max_usage_in_bytes_test 4 TINFO: Running memcg_process --mmap-anon -s 4194304
memcg_max_usage_in_bytes_test 4 TINFO: Warming up pid: 728040
memcg_max_usage_in_bytes_test 4 TINFO: Process is still here after warm up: 728040
memcg_max_usage_in_bytes_test 4 TFAIL: memory.memsw.max_usage_in_bytes is 4456448, 4194304 expected
memcg_max_usage_in_bytes_test 4 TFAIL: memory.memsw.max_usage_in_bytes is 258048, 0 expected
```
#### memcg_use_hierarchy
```
memcg_use_hierarchy_test 1 TINFO: timeout per run is 0h 50m 0s
memcg_use_hierarchy_test 1 TINFO: set /dev/memcg/memory.use_hierarchy to 0 failed
memcg_use_hierarchy_test 1 TINFO: test if one of the ancestors goes over its limit, the proces will be killed
mkdir: cannot create directory ‘subgroup’: Cannot allocate memory
/opt/ltp/testcases/bin/memcg_use_hierarchy_test.sh: line 22: cd: subgroup: No such file or directory
memcg_use_hierarchy_test 1 TINFO: Running memcg_process --mmap-lock1 -s 8192
memcg_use_hierarchy_test 1 TFAIL: process  is not killed
rmdir: failed to remove 'subgroup': No such file or directory
memcg_use_hierarchy_test 2 TINFO: test Enabling will fail if the cgroup already has other cgroups
memcg_use_hierarchy_test 2 TCONF: Test requires root cgroup memory.use_hierarchy=0
```
#### memcg_usage_in_bytes
```
memcg_usage_in_bytes_test 1 TINFO: timeout per run is 0h 50m 0s
memcg_usage_in_bytes_test 1 TINFO: set /dev/memcg/memory.use_hierarchy to 0 failed
memcg_usage_in_bytes_test 1 TINFO: Test memory.usage_in_bytes
memcg_usage_in_bytes_test 1 TINFO: Running memcg_process --mmap-anon -s 4194304
memcg_usage_in_bytes_test 1 TINFO: Warming up pid: 728551
memcg_usage_in_bytes_test 1 TINFO: Process is still here after warm up: 728551
memcg_usage_in_bytes_test 1 TFAIL: memory.usage_in_bytes is 4456448, 4194304 expected
memcg_usage_in_bytes_test 2 TINFO: Test memory.memsw.usage_in_bytes
memcg_usage_in_bytes_test 2 TINFO: Running memcg_process --mmap-anon -s 4194304
memcg_usage_in_bytes_test 2 TINFO: Warming up pid: 728565
memcg_usage_in_bytes_test 2 TINFO: Process is still here after warm up: 728565
memcg_usage_in_bytes_test 2 TFAIL: memory.memsw.usage_in_bytes is 4456448, 4194304 expected
```
#### df01_ext2_sh
```
df01 1 TINFO: timeout per run is 0h 50m 0s
tst_device.c:268: TINFO: Using test device LTP_DEV='/dev/vdc1'
df01 1 TINFO: Formatting /dev/vdc1 with ext2 extra opts=''
df01 1 TPASS: 'df -P' passed.
df01 2 TPASS: 'df -a -P' passed.
df01 3 TPASS: 'df -i -P' passed.
df01 4 TPASS: 'df -k -P' passed.
df01 5 TPASS: 'df -t ext2 -P' passed.
df01 6 TPASS: 'df -T -P' passed.
df01 7 TPASS: 'df -v /dev/vdc1 -P' passed.
df01 8 TPASS: 'df -h' passed.
df01 9 TPASS: 'df -H' passed.
df01 10 TPASS: 'df -m' passed.
df01 11 TPASS: 'df --version' passed.
df01 12 TPASS: 'df -x ext2 -P' passed.
tst_device.c:203: TWARN: ioctl(/dev/vdc1, LOOP_CLR_FD, 0) unexpectedly failed with: ENOTTY

Usage: tst_device acquire [size [filename]]
   or: tst_device release /path/to/device

df01 13 TWARN: Failed to release device '/dev/vdc1'
```
#### df01_ext3_sh
```
df01 1 TINFO: timeout per run is 0h 50m 0s
tst_device.c:268: TINFO: Using test device LTP_DEV='/dev/vdc1'
df01 1 TINFO: Formatting /dev/vdc1 with ext3 extra opts=''
df01 1 TPASS: 'df -P' passed.
df01 2 TPASS: 'df -a -P' passed.
df01 3 TPASS: 'df -i -P' passed.
df01 4 TPASS: 'df -k -P' passed.
df01 5 TPASS: 'df -t ext3 -P' passed.
df01 6 TPASS: 'df -T -P' passed.
df01 7 TPASS: 'df -v /dev/vdc1 -P' passed.
df01 8 TPASS: 'df -h' passed.
df01 9 TPASS: 'df -H' passed.
df01 10 TPASS: 'df -m' passed.
df01 11 TPASS: 'df --version' passed.
df01 12 TPASS: 'df -x ext3 -P' passed.
tst_device.c:203: TWARN: ioctl(/dev/vdc1, LOOP_CLR_FD, 0) unexpectedly failed with: ENOTTY

Usage: tst_device acquire [size [filename]]
   or: tst_device release /path/to/device

df01 13 TWARN: Failed to release device '/dev/vdc1'
```
#### df01_ext4_sh
```
df01 1 TINFO: timeout per run is 0h 50m 0s
tst_device.c:268: TINFO: Using test device LTP_DEV='/dev/vdc1'
df01 1 TINFO: Formatting /dev/vdc1 with ext4 extra opts=''
df01 1 TPASS: 'df -P' passed.
df01 2 TPASS: 'df -a -P' passed.
df01 3 TPASS: 'df -i -P' passed.
df01 4 TPASS: 'df -k -P' passed.
df01 5 TPASS: 'df -t ext4 -P' passed.
df01 6 TPASS: 'df -T -P' passed.
df01 7 TPASS: 'df -v /dev/vdc1 -P' passed.
df01 8 TPASS: 'df -h' passed.
df01 9 TPASS: 'df -H' passed.
df01 10 TPASS: 'df -m' passed.
df01 11 TPASS: 'df --version' passed.
df01 12 TPASS: 'df -x ext4 -P' passed.
tst_device.c:203: TWARN: ioctl(/dev/vdc1, LOOP_CLR_FD, 0) unexpectedly failed with: ENOTTY

Usage: tst_device acquire [size [filename]]
   or: tst_device release /path/to/device

df01 13 TWARN: Failed to release device '/dev/vdc1'
```
#### df01_xfs_sh
```
df01 1 TINFO: timeout per run is 0h 50m 0s
tst_device.c:268: TINFO: Using test device LTP_DEV='/dev/vdc1'
df01 1 TINFO: Formatting /dev/vdc1 with xfs extra opts=''
mount: /ltp/tmp/ltp-79jkrem1Ia/LTP_df01.8ZhLDn2reU/mntpoint: unknown filesystem type 'xfs'.
df01 1 TCONF: Cannot mount xfs type, missing driver?
df01 1 TINFO: The /dev/vdc1 is not mounted, skipping umount
tst_device.c:203: TWARN: ioctl(/dev/vdc1, LOOP_CLR_FD, 0) unexpectedly failed with: ENOTTY

Usage: tst_device acquire [size [filename]]
   or: tst_device release /path/to/device

df01 1 TWARN: Failed to release device '/dev/vdc1'
```
#### df01_vfat_sh
```
df01 1 TINFO: timeout per run is 0h 50m 0s
tst_device.c:268: TINFO: Using test device LTP_DEV='/dev/vdc1'
df01 1 TINFO: Formatting /dev/vdc1 with vfat extra opts=''
df01 1 TPASS: 'df -P' passed.
df01 2 TPASS: 'df -a -P' passed.
df01 3 TPASS: 'df -i -P' passed.
df01 4 TPASS: 'df -k -P' passed.
df01 5 TPASS: 'df -t vfat -P' passed.
df01 6 TPASS: 'df -T -P' passed.
df01 7 TPASS: 'df -v /dev/vdc1 -P' passed.
df01 8 TPASS: 'df -h' passed.
df01 9 TPASS: 'df -H' passed.
df01 10 TPASS: 'df -m' passed.
df01 11 TPASS: 'df --version' passed.
df01 12 TPASS: 'df -x vfat -P' passed.
tst_device.c:203: TWARN: ioctl(/dev/vdc1, LOOP_CLR_FD, 0) unexpectedly failed with: ENOTTY

Usage: tst_device acquire [size [filename]]
   or: tst_device release /path/to/device

df01 13 TWARN: Failed to release device '/dev/vdc1'
```
#### df01_exfat_sh
```
df01 1 TINFO: timeout per run is 0h 50m 0s
tst_device.c:268: TINFO: Using test device LTP_DEV='/dev/vdc1'
df01 1 TCONF: 'mkfs.exfat' not found
df01 1 TINFO: The /dev/vdc1 is not mounted, skipping umount
  tst_device.c:203: TWARN: ioctl(/dev/vdc1, LOOP_CLR_FD, 0) unexpectedly failed with: ENOTTY

Usage: tst_device acquire [size [filename]]
   or: tst_device release /path/to/device

df01 1 TWARN: Failed to release device '/dev/vdc1'
```
#### df01_ntfs_sh
```
df01 1 TINFO: timeout per run is 0h 50m 0s
tst_device.c:268: TINFO: Using test device LTP_DEV='/dev/vdc1'
df01 1 TINFO: Formatting /dev/vdc1 with ntfs extra opts=''
df01 1 TPASS: 'df -P' passed.
df01 2 TPASS: 'df -a -P' passed.
df01 3 TPASS: 'df -i -P' passed.
df01 4 TPASS: 'df -k -P' passed.
df01 5 TPASS: 'df -t fuseblk -P' passed.
df01 6 TPASS: 'df -T -P' passed.
df01 7 TPASS: 'df -v /dev/vdc1 -P' passed.
df01 8 TPASS: 'df -h' passed.
df01 9 TPASS: 'df -H' passed.
df01 10 TPASS: 'df -m' passed.
df01 11 TPASS: 'df --version' passed.
df01 12 TPASS: 'df -x fuseblk -P' passed.
tst_device.c:203: TWARN: ioctl(/dev/vdc1, LOOP_CLR_FD, 0) unexpectedly failed with: ENOTTY

Usage: tst_device acquire [size [filename]]
   or: tst_device release /path/to/device

df01 13 TWARN: Failed to release device '/dev/vdc1'
```
#### mkfs01_sh
```
mkfs01 1 TINFO: timeout per run is 0h 50m 0s
tst_device.c:268: TINFO: Using test device LTP_DEV='/dev/vdc1'
mkfs01 1 TPASS: 'mkfs   /dev/vdc1 ' passed.
mkfs01 2 TPASS: 'mkfs   /dev/vdc1 16000' passed.
mkfs01 3 TPASS: 'mkfs  -c /dev/vdc1 ' passed.
mkfs01 4 TPASS: 'mkfs -V   ' passed.
mkfs01 5 TPASS: 'mkfs -h   ' passed.
tst_device.c:203: TWARN: ioctl(/dev/vdc1, LOOP_CLR_FD, 0) unexpectedly failed with: ENOTTY

Usage: tst_device acquire [size [filename]]
   or: tst_device release /path/to/device

mkfs01 6 TWARN: Failed to release device '/dev/vdc1'
```
#### mkfs01_ext2_sh
```
mkfs01 1 TINFO: timeout per run is 0h 50m 0s
tst_device.c:268: TINFO: Using test device LTP_DEV='/dev/vdc1'
mkfs01 1 TPASS: 'mkfs -t ext2  /dev/vdc1 ' passed.
mkfs01 2 TPASS: 'mkfs -t ext2  /dev/vdc1 16000' passed.
mkfs01 3 TPASS: 'mkfs -t ext2 -c /dev/vdc1 ' passed.
mkfs01 4 TPASS: 'mkfs -V   ' passed.
mkfs01 5 TPASS: 'mkfs -h   ' passed.
tst_device.c:203: TWARN: ioctl(/dev/vdc1, LOOP_CLR_FD, 0) unexpectedly failed with: ENOTTY

Usage: tst_device acquire [size [filename]]
   or: tst_device release /path/to/device

mkfs01 6 TWARN: Failed to release device '/dev/vdc1'
```
#### mkfs01_ext3_sh
```
mkfs01 1 TINFO: timeout per run is 0h 50m 0s
tst_device.c:268: TINFO: Using test device LTP_DEV='/dev/vdc1'
mkfs01 1 TPASS: 'mkfs -t ext3  /dev/vdc1 ' passed.
mkfs01 2 TFAIL: 'mkfs -t ext3  /dev/vdc1 16000' failed, not expected.
mkfs01 3 TPASS: 'mkfs -t ext3 -c /dev/vdc1 ' passed.
mkfs01 4 TPASS: 'mkfs -V   ' passed.
mkfs01 5 TPASS: 'mkfs -h   ' passed.
tst_device.c:203: TWARN: ioctl(/dev/vdc1, LOOP_CLR_FD, 0) unexpectedly failed with: ENOTTY

Usage: tst_device acquire [size [filename]]
   or: tst_device release /path/to/device

mkfs01 6 TWARN: Failed to release device '/dev/vdc1'
```
#### mkfs01_ext4_sh
```
mkfs01 1 TINFO: timeout per run is 0h 50m 0s
tst_device.c:268: TINFO: Using test device LTP_DEV='/dev/vdc1'
mkfs01 1 TPASS: 'mkfs -t ext4  /dev/vdc1 ' passed.
mkfs01 2 TFAIL: 'mkfs -t ext4  /dev/vdc1 16000' failed, not expected.
mkfs01 3 TPASS: 'mkfs -t ext4 -c /dev/vdc1 ' passed.
mkfs01 4 TPASS: 'mkfs -V   ' passed.
mkfs01 5 TPASS: 'mkfs -h   ' passed.
tst_device.c:203: TWARN: ioctl(/dev/vdc1, LOOP_CLR_FD, 0) unexpectedly failed with: ENOTTY

Usage: tst_device acquire [size [filename]]
   or: tst_device release /path/to/device

mkfs01 6 TWARN: Failed to release device '/dev/vdc1'
```
#### mkfs01_xfs_sh
```
mkfs01 1 TINFO: timeout per run is 0h 50m 0s
tst_device.c:268: TINFO: Using test device LTP_DEV='/dev/vdc1'
mkfs01 1 TPASS: 'mkfs -t xfs  -f /dev/vdc1 ' passed.
mkfs01 2 TCONF: 'mkfs -t xfs  -f /dev/vdc1 16000' not supported.
mkfs01 3 TCONF: 'mkfs -t xfs -c -f /dev/vdc1 ' not supported.
mkfs01 4 TPASS: 'mkfs -V   ' passed.
mkfs01 5 TPASS: 'mkfs -h   ' passed.
tst_device.c:203: TWARN: ioctl(/dev/vdc1, LOOP_CLR_FD, 0) unexpectedly failed with: ENOTTY

Usage: tst_device acquire [size [filename]]
   or: tst_device release /path/to/device

mkfs01 6 TWARN: Failed to release device '/dev/vdc1'
```
#### mkfs01_btrfs_sh
```
mkfs01 1 TINFO: timeout per run is 0h 50m 0s
tst_device.c:268: TINFO: Using test device LTP_DEV='/dev/vdc1'
mkfs01 1 TPASS: 'mkfs -t btrfs  -f /dev/vdc1 ' passed.
mkfs01 2 TCONF: 'mkfs -t btrfs  -f /dev/vdc1 16000' not supported.
mkfs01 3 TCONF: 'mkfs -t btrfs -c -f /dev/vdc1 ' not supported.
mkfs01 4 TPASS: 'mkfs -V   ' passed.
mkfs01 5 TPASS: 'mkfs -h   ' passed.
tst_device.c:203: TWARN: ioctl(/dev/vdc1, LOOP_CLR_FD, 0) unexpectedly failed with: ENOTTY

Usage: tst_device acquire [size [filename]]
   or: tst_device release /path/to/device

mkfs01 6 TWARN: Failed to release device '/dev/vdc1'
```
#### mkfs01_minix_sh
```
mkfs01 1 TINFO: timeout per run is 0h 50m 0s
tst_device.c:268: TINFO: Using test device LTP_DEV='/dev/vdc1'
mkfs01 1 TPASS: 'mkfs -t minix  /dev/vdc1 ' passed.
mount: /ltp/tmp/ltp-79jkrem1Ia/LTP_mkfs01.526E1AJkwV/mntpoint: unknown filesystem type 'minix'.
mkfs01 2 TCONF: Cannot mount minix type, missing driver?
tst_device.c:203: TWARN: ioctl(/dev/vdc1, LOOP_CLR_FD, 0) unexpectedly failed with: ENOTTY

Usage: tst_device acquire [size [filename]]
   or: tst_device release /path/to/device

mkfs01 2 TWARN: Failed to release device '/dev/vdc1'
```
#### mkfs01_msdos_sh
```
mkfs01 1 TINFO: timeout per run is 0h 50m 0s
tst_device.c:268: TINFO: Using test device LTP_DEV='/dev/vdc1'
mkfs01 1 TPASS: 'mkfs -t msdos  /dev/vdc1 ' passed.
mkfs01 2 TFAIL: 'mkfs -t msdos  /dev/vdc1 16000' failed.
Warning: block count mismatch: found 1047552 but assuming 16000.
WARNING: Number of clusters for 32 bit FAT is less then suggested minimum.
mkfs.msdos: Attempting to create a too small or a too large filesystem
mkfs.fat 4.2 (2021-01-31)
mkfs01 3 TPASS: 'mkfs -t msdos -c /dev/vdc1 ' passed.
mkfs01 4 TPASS: 'mkfs -V   ' passed.
mkfs01 5 TPASS: 'mkfs -h   ' passed.
tst_device.c:203: TWARN: ioctl(/dev/vdc1, LOOP_CLR_FD, 0) unexpectedly failed with: ENOTTY

Usage: tst_device acquire [size [filename]]
   or: tst_device release /path/to/device

mkfs01 6 TWARN: Failed to release device '/dev/vdc1'
```
#### mkfs01_vfat_sh
```
mkfs01 1 TINFO: timeout per run is 0h 50m 0s
tst_device.c:268: TINFO: Using test device LTP_DEV='/dev/vdc1'
mkfs01 1 TPASS: 'mkfs -t vfat  /dev/vdc1 ' passed.
mkfs01 2 TFAIL: 'mkfs -t vfat  /dev/vdc1 16000' failed.
Warning: block count mismatch: found 1047552 but assuming 16000.
WARNING: Number of clusters for 32 bit FAT is less then suggested minimum.
mkfs.vfat: Attempting to create a too small or a too large filesystem
mkfs.fat 4.2 (2021-01-31)
mkfs01 3 TPASS: 'mkfs -t vfat -c /dev/vdc1 ' passed.
mkfs01 4 TPASS: 'mkfs -V   ' passed.
mkfs01 5 TPASS: 'mkfs -h   ' passed.
tst_device.c:203: TWARN: ioctl(/dev/vdc1, LOOP_CLR_FD, 0) unexpectedly failed with: ENOTTY

Usage: tst_device acquire [size [filename]]
   or: tst_device release /path/to/device

mkfs01 6 TWARN: Failed to release device '/dev/vdc1'
```
#### mkfs01_ntfs_sh
```
mkfs01 1 TINFO: timeout per run is 0h 50m 0s
tst_device.c:268: TINFO: Using test device LTP_DEV='/dev/vdc1'
mkfs01 1 TPASS: 'mkfs -t ntfs  /dev/vdc1 ' passed.
mkfs01 2 TPASS: 'mkfs -t ntfs  /dev/vdc1 16000' passed.
mkfs01 3 TCONF: 'mkfs -t ntfs -c /dev/vdc1 ' not supported.
mkfs01 4 TPASS: 'mkfs -V   ' passed.
mkfs01 5 TPASS: 'mkfs -h   ' passed.
tst_device.c:203: TWARN: ioctl(/dev/vdc1, LOOP_CLR_FD, 0) unexpectedly failed with: ENOTTY

Usage: tst_device acquire [size [filename]]
   or: tst_device release /path/to/device

mkfs01 6 TWARN: Failed to release device '/dev/vdc1'
```
#### mkswap01_sh
```
mkswap01 1 TINFO: timeout per run is 0h 50m 0s
tst_device.c:268: TINFO: Using test device LTP_DEV='/dev/vdc1'
mkswap01 1 TPASS: 'mkswap   /dev/vdc1 ' passed.
mkswap01 2 TPASS: 'mkswap   /dev/vdc1 1047548' passed.
mkswap01 3 TINFO: Can not do swapon on /dev/vdc1.
mkswap01 3 TINFO: Device size specified by 'mkswap' greater than real size.
mkswap01 3 TINFO: Swapon failed expectedly.
mkswap01 3 TPASS: 'mkswap -f  /dev/vdc1 1047556' passed.
mkswap01 4 TPASS: 'mkswap -c  /dev/vdc1 ' passed.
mkswap01 5 TINFO: Can not do swapon on /dev/vdc1.
mkswap01 5 TINFO: Page size specified by 'mkswap -p' is not equal to system's page size.
mkswap01 5 TINFO: Swapon failed expectedly.
mkswap01 5 TPASS: 'mkswap -p 2048 /dev/vdc1 ' passed.
mkswap01 6 TPASS: 'mkswap -L ltp_testswap /dev/vdc1 ' passed.
mkswap01 7 TPASS: 'mkswap -v1  /dev/vdc1 ' passed.
mkswap01 8 TPASS: 'mkswap -U 901ab794-7f8d-418b-94f7-ac6b3d22c630 /dev/vdc1 ' passed.
mkswap01 9 TPASS: 'mkswap -V  /dev/vdc1 ' passed.
mkswap01 10 TPASS: 'mkswap -h  /dev/vdc1 ' passed.
tst_device.c:203: TWARN: ioctl(/dev/vdc1, LOOP_CLR_FD, 0) unexpectedly failed with: ENOTTY

Usage: tst_device acquire [size [filename]]
   or: tst_device release /path/to/device

mkswap01 11 TWARN: Failed to release device '/dev/vdc1'
```
#### cve-2018-12896
```
tst_kconfig.c:64: TINFO: Parsing kernel config '/proc/config.gz'
tst_test.c:1289: TINFO: Timeout per run is 0h 50m 00s
timer_settime03.c:105: TFAIL: Timer overrun counter is wrong: 767; expected 2147483647 or negative number

HINT: You _MAY_ be missing kernel fixes, see:

https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=78c9c4dfbf8c

HINT: You _MAY_ be vulnerable to CVE(s), see:

https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-12896
```
#### tpci
```
test_pci    1  TPASS  :  PCI bus 00 slot 08 : Test-case '1'
test_pci    2  TPASS  :  PCI bus 00 slot 08 : Test-case '2'
test_pci    3  TPASS  :  PCI bus 00 slot 08 : Test-case '3'
test_pci    4  TPASS  :  PCI bus 00 slot 08 : Test-case '4'
test_pci    5  TPASS  :  PCI bus 00 slot 08 : Test-case '5'
test_pci    6  TPASS  :  PCI bus 00 slot 08 : Test-case '6'
test_pci    7  TPASS  :  PCI bus 00 slot 08 : Test-case '7'
test_pci    8  TPASS  :  PCI bus 00 slot 08 : Test-case '8'
test_pci    9  TPASS  :  PCI bus 00 slot 08 : Test-case '9'
test_pci   10  TPASS  :  PCI bus 00 slot 08 : Test-case '10'
test_pci   11  TPASS  :  PCI bus 00 slot 08 : Test-case '11'
test_pci   12  TFAIL  :  tpci.c:73: PCI bus 00 slot 08 : Test-case '12'
test_pci   13  TPASS  :  PCI bus 00 slot 08 : Test-case '13'
test_pci   14  TPASS  :  PCI bus 00 slot 08 : Test-case '14'
test_pci   15  TPASS  :  PCI bus 00 slot 08 : Test-case '15'
test_pci   16  TCONF  :  tpci.c:73: PCI bus 00 slot 08 : Test-case '16'
test_pci   17  TPASS  :  PCI bus 00 slot 10 : Test-case '1'
test_pci   18  TPASS  :  PCI bus 00 slot 10 : Test-case '2'
test_pci   19  TPASS  :  PCI bus 00 slot 10 : Test-case '3'
test_pci   20  TPASS  :  PCI bus 00 slot 10 : Test-case '4'
test_pci   21  TPASS  :  PCI bus 00 slot 10 : Test-case '5'
test_pci   22  TPASS  :  PCI bus 00 slot 10 : Test-case '6'
test_pci   23  TPASS  :  PCI bus 00 slot 10 : Test-case '7'
test_pci   24  TPASS  :  PCI bus 00 slot 10 : Test-case '8'
test_pci   25  TPASS  :  PCI bus 00 slot 10 : Test-case '9'
test_pci   26  TPASS  :  PCI bus 00 slot 10 : Test-case '10'
test_pci   27  TPASS  :  PCI bus 00 slot 10 : Test-case '11'
test_pci   28  TPASS  :  PCI bus 00 slot 10 : Test-case '12'
test_pci   29  TPASS  :  PCI bus 00 slot 10 : Test-case '13'
test_pci   30  TPASS  :  PCI bus 00 slot 10 : Test-case '14'
test_pci   31  TPASS  :  PCI bus 00 slot 10 : Test-case '15'
test_pci   32  TPASS  :  PCI bus 00 slot 10 : Test-case '16'
```

### 部分报错跟踪

#### leapsec01

报错逻辑在leapsec01.c的第83行，即adjtimex_status函数中：

```c
static void adjtimex_status(struct timex *tx, int status)
{
	const char *const msgs[6] = {
		"clock synchronized",
		"insert leap second",
		"delete leap second",
		"leap second in progress",
		"leap second has occurred",
		"clock not synchronized",
	};

	int ret;
	struct timespec now;

	tx->modes = ADJ_STATUS;
	tx->status = status;
	ret = adjtimex(tx);
	now.tv_sec = tx->time.tv_sec;
	now.tv_nsec = tx->time.tv_usec * 1000;

	if ((tx->status & status) != status)
		tst_brk(TBROK, "adjtimex status %d not set", status);
	else if (ret < 0)
		tst_brk(TBROK | TERRNO, "adjtimex");
	else if (ret < 6)
		tst_res(TINFO, "%s adjtimex: %s", strtime(&now), msgs[ret]);
	else
		tst_res(TINFO, "%s adjtimex: clock state %d",
			 strtime(&now), ret);
}
```

即调用了adjtimex函数之后结构体tx的status成员异常。使用gdb查看报错之前tx结构体的变化：

刚进入adjtimex_status函数时的tx结构体的值：

![](https://raw.githubusercontent.com/l0tk3/PLCT/main/WrokReport/week0/LTP/LTPimg/tx_in_run_leapsec.png)

经过adjtimex函数之后的tx结构体：

![](https://raw.githubusercontent.com/l0tk3/PLCT/main/WrokReport/week0/LTP/LTPimg/tx_in_adjtimex_status.png)

#### finit_module02

报错部分

```c
openat(AT_FDCWD, "/opt/ltp/testcases/bin/finit_module.ko", O_WRONLY|O_CLOEXEC) = 4
finit_module(4, "", 0)    = -1 EBADF (Bad file descriptor)
```

#### getxattr04

报错部分：

```c
mkdirat(AT_FDCWD, "mntpoint", 0777)
mount("/dev/vdc1", "mntpoint", "xfs", 0, NULL) = -1 ENODEV (No such device)
```

#### timer_settime03

报错部分

```c
timer_settime(0, TIMER_ABSTIME, {it_interval={tv_sec=0, tv_nsec=1}, it_value={tv_sec=1684312121, tv_nsec=337498640}}, NULL) = 0
timer_getoverrun(0)       = 767
```

#### perf_event_open01

报错部分：

```c
perf_event_open({type=PERF_TYPE_HARDWARE, size=PERF_ATTR_SIZE_VER7, config=PERF_COUNT_HW_INSTRUCTIONS, sample_period=0, sample_type=0, read_format=0, disabled=1, exclude_kernel=1, exclude_hv=1, precise_ip=0 /* arbitrary skid */, ...}, 0, -1, -1, 0) = -1 EINVAL (Invalid argument)
```

#### vma05

看上去是pthread_kill+16这个地方的跳转会影响栈回溯中的数据

跳转前：

![](https://raw.githubusercontent.com/l0tk3/PLCT/main/WrokReport/week0/LTP/LTPimg/pthread_kill.png)

跳转后：

![](https://raw.githubusercontent.com/l0tk3/PLCT/main/WrokReport/week0/LTP/LTPimg/pthread_kill1.png)

#### df01、mkswap01、mkfs01

strace跟踪

```c
[pid 1837603] execve("/opt/ltp/testcases/bin/tst_device", ["tst_device", "release", "/dev/vdc1"], 0xaaaaaac833b1a0 /* 41 vars */) = 0
[pid 1837603] brk(NULL)                 = 0x36000
[pid 1837603] faccessat(AT_FDCWD, "/etc/ld.so.preload", R_OK) = -1 ENOENT (No such file or directory)
[pid 1837603] openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3
[pid 1837603] newfstatat(3, "", {st_mode=S_IFREG|0644, st_size=23643, ...}, AT_EMPTY_PATH) = 0
[pid 1837603] mmap(NULL, 23643, PROT_READ, MAP_PRIVATE, 3, 0) = 0xffffffba616000
[pid 1837603] close(3)                  = 0
[pid 1837603] openat(AT_FDCWD, "/usr/lib64/libc.so.6", O_RDONLY|O_CLOEXEC) = 3
[pid 1837603] read(3, "\177ELF\2\1\1\3\0\0\0\0\0\0\0\0\3\0\363\0\1\0\0\0\300m\2\0\0\0\0\0"..., 832) = 832
[pid 1837603] newfstatat(3, "", {st_mode=S_IFREG|0755, st_size=1616792, ...}, AT_EMPTY_PATH) = 0
[pid 1837603] mmap(NULL, 8192, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0xffffffba614000
[pid 1837603] mmap(NULL, 1659064, PROT_READ|PROT_EXEC, MAP_PRIVATE|MAP_DENYWRITE, 3, 0) = 0xffffffba47e000
[pid 1837603] mprotect(0xffffffba601000, 4096, PROT_NONE) = 0
[pid 1837603] mmap(0xffffffba602000, 20480, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x183000) = 0xffffffba602000
[pid 1837603] mmap(0xffffffba607000, 49336, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) = 0xffffffba607000
[pid 1837603] close(3)                  = 0
[pid 1837603] set_tid_address(0xffffffba614d30) = 1837603
[pid 1837603] set_robust_list(0xffffffba614d40, 24) = 0
[pid 1837603] mprotect(0xffffffba602000, 12288, PROT_READ) = 0
[pid 1837603] mprotect(0x2f000, 4096, PROT_READ) = 0
[pid 1837603] mprotect(0xffffffba644000, 4096, PROT_READ) = 0
[pid 1837603] prlimit64(0, RLIMIT_STACK, NULL, {rlim_cur=8192*1024, rlim_max=RLIM64_INFINITY}) = 0
[pid 1837603] munmap(0xffffffba616000, 23643) = 0
[pid 1837603] openat(AT_FDCWD, "/dev/vdc1", O_RDONLY) = 3
[pid 1837603] ioctl(3, LOOP_CLR_FD)     = -1 ENOTTY (Inappropriate ioctl for device)
[pid 1837603] ioctl(2, TCGETS, {c_iflag=ICRNL|IXON|IXANY|IMAXBEL|IUTF8, c_oflag=NL0|CR0|TAB0|BS0|VT0|FF0|OPOST|ONLCR, c_cflag=B38400|CS8|CREAD, c_lflag=ISIG|ICANON|ECHO|ECHOE|ECHOK|IEXTEN|ECHOCTL|ECHOKE|PENDIN, ...}) = 0
[pid 1837603] write(2, "tst_device.c:203: \33[1;35mTWARN: "..., 102tst_device.c:203: TWARN: ioctl(/dev/vdc1, LOOP_CLR_FD, 0) unexpectedly failed with: ENOTTY
) = 102
[pid 1837603] close(3)                  = 0
[pid 1837603] write(2, "\nUsage: tst_device acquire [size"..., 45
Usage: tst_device acquire [size [filename]]
) = 45
[pid 1837603] write(2, "   or: tst_device release /path/"..., 43   or: tst_device release /path/to/device
) = 43
```

发现为调用```tst_device release /dev/vdc1```报错，报错信息为```ioctl(/dev/vdc1, LOOP_CLR_FD, 0) unexpectedly failed with: ENOTTY```。报错函数为ltp/lib/tst_device.c中的tst_detach_device_by_fd：

```c
int tst_detach_device_by_fd(const char *dev, int dev_fd)
{
	int ret, i;

	/* keep trying to clear LOOPDEV until we get ENXIO, a quick succession
	 * of attach/detach might not give udev enough time to complete
	 */
	for (i = 0; i < 40; i++) {
		ret = ioctl(dev_fd, LOOP_CLR_FD, 0);

		if (ret && (errno == ENXIO))
			return 0;

		if (ret && (errno != EBUSY)) {
			tst_resm(TWARN,
				 "ioctl(%s, LOOP_CLR_FD, 0) unexpectedly failed with: %s",
				 dev, tst_strerrno(errno));
			return 1;
		}

		usleep(50000);
	}

	tst_resm(TWARN,
		"ioctl(%s, LOOP_CLR_FD, 0) no ENXIO for too long", dev);
	return 1;
}
```



