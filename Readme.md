# 教工运动会分队投票

教师自己投票分队，但大家都会跟着体育组，不是吗？

## 安装

1. Python 3.8，傻逼mysqldb在3.12上编译不了，大概是我水平不大行
2. 安装项目依赖：

    ```bash
    pip install -r requirements.txt
    ```

3. 在 MySQL 中创建 `TeacherSports` 数据库，并创建`voting_records` 表：

    ```bash
    source ./sql.sql
    ```
4. 修改人数，人名，mysql连接地址：

    `./template/index.html`内：70，71，75，78行

    `./main.py`内：7，34，42行

## 运行

运行 Flask 应用：

```bash
python app.py