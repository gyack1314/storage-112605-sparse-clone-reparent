# 产线基线镜像的稀疏克隆与原地换父

镜像 image/rev 是不可变的封存内容，未声明的块为空。clone 是独立卷。null 表示本地明确清零。at 只表示事件到达时间。

## 输入消息

每个 JSONL 文件是一段独立输入记录。每行包括整数秒点 at、消息名称 kind 与对象 record。at 代表中间件收到消息的时刻，同一秒内按行序提交。业务时间和对应回执引用写在 record 中。

- **image**　提交 image、rev、blocks 与 size。blocks 的键是从 0 开始的块号。 先据 size 确认范围，再解释范围内未列出的块。
- **clone**　从 image/rev 创建 volume。
- **write**　对 volume 的 block 写 text；null 明确清零。request 是重试身份。
- **read**　打开 volume/block 的 reader；查询与释放均使用此身份。
- **close**　结束读取。
- **rebase**　尝试将 volume 换父为 image/rev，budget 为允许新增块数。
- **material**　仿真介质确认对应 rebase 的块字节已经分配。 text 为介质实际返回的字节。
- **cutover**　尝试提交 rebase。
- **fault**　明确损坏 image/rev 的 block。
- **reclaim**　尝试释放 image/rev。
- **restart**　服务重启。
- **inspect**　查询 volume 或镜像。

## 示例

- clear-races-rebase.jsonl
- unknown-block-must-not-be-zero.jsonl

## 读取演练资料

运行环境为 Python 3.11，只使用标准库。在根目录运行以下命令可核对文件格式及读取接口。

    python3 scenario_reader.py examples
    python3 -m unittest discover -v

资料读取器会按文件统计各类参与方消息的数量。演练记录只描述各参与方交给系统的输入。
