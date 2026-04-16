# Career Agent Backend

## 📖 项目简介

**Career Agent** 是一款基于人工智能的大学生职业规划智能体，旨在帮助学生解决职业规划中的信息不对称、自我认知模糊、规划落地难等问题。系统通过大模型分析海量招聘数据，构建岗位典型画像；同时根据学生上传的简历或手动录入信息，生成个人能力画像；并基于多维度的匹配算法，为学生推荐最匹配的职业方向，生成详细的职业发展报告（含区域机会分析、晋升/换岗路径、学习资源推荐等）。项目融合了自然语言处理、知识图谱、数据可视化等技术，为学生提供专业、个性化的职业规划服务。

---

## ✨ 功能特性

- **双主线设计**：求职主线（简历驱动）与探索主线（手动录入驱动）并存，数据共享，用户可随时切换。
- **岗位画像生成**：从职位描述中提取技能、证书、能力评分（创新、学习、抗压、沟通）、学历/专业/工作经验等13个维度的要求，并聚合形成岗位典型画像。
- **学生画像生成**：支持上传 PDF/Word/TXT 格式简历，大模型自动解析生成相同维度的能力画像，并给出综合竞争力评分；同时支持手动录入基本信息、项目、实习、竞赛等经历，动态更新画像。
- **人岗匹配**：从基础要求、职业技能、职业素养、发展潜力四个维度计算匹配度，采用技能标准化和模糊匹配算法，确保关键技能匹配准确率 ≥80%。
- **职业发展报告**：一键生成 Word 报告，包含匹配分析、雷达图可视化、区域机会（薪资/需求/城市）、PDCA 发展计划、学习资源推荐、岗位调动建议等。
- **岗位图谱**：构建岗位间的晋升路径和换岗路径，存储于 Neo4j 图数据库，提供可视化查询接口。
- **区域薪资分析**：按东部、中部、西部、东北四大区域统计岗位的招聘数量、平均薪资、主要城市，帮助学生了解地域差异。
- **报告编辑与润色**：支持前端预览报告内容，用户可手动编辑并导出；提供文本润色接口，支持自定义润色指令。
- **历史版本管理**：每次上传简历或手动更新经历时自动保存版本，支持回溯查看。
- **用户认证与数据隔离**：JWT 令牌认证，每个用户拥有独立账户，所有个人数据严格隔离。
- **职业路径推荐与动态调整**：探索主线中，根据学生画像推荐2-3条职业路径，选择后生成 PDCA 发展计划；支持动态刷新匹配度，并提供备选路径建议。
- **高准确性保证**：画像生成采用 few-shot 示例、后处理校验、置信度自评+自动重试；技能匹配使用同义词库 + 模糊匹配；配套评估脚本可抽样验证准确率。

---

## 🛠️ 技术栈

| 类别         | 技术                                   |
|--------------|----------------------------------------|
| 后端框架     | FastAPI, Uvicorn                       |
| 数据库       | MySQL (SQLAlchemy), Neo4j              |
| 大模型       | 阿里云 DashScope (千问)                |
| 文件解析     | PyPDF2, python-docx                    |
| 报告生成     | python-docx, matplotlib                |
| 数据处理     | pandas, openpyxl, tqdm                 |
| 认证         | JWT (python-jose), passlib[bcrypt]     |
| 部署         | Docker (可选), Nginx (可选)            |

---

## 🏗️ 系统架构
[前端] → [FastAPI 后端] → [大模型服务] → [MySQL/Neo4j]
↓
[Word 报告生成]

text

- 前端通过 RESTful API 与后端交互。
- 后端负责数据处理、模型调用、数据库操作。
- 大模型（千问）用于文本分析、画像生成、报告润色。
- MySQL 存储岗位数据、画像、学生信息、用户账户、历史版本。
- Neo4j 存储岗位图谱关系。

---

## ⚙️ 环境要求

- Python 3.8+
- MySQL 5.7+（推荐 8.0）
- Neo4j 4.4+（可选，若不需要图谱功能可跳过）
- 阿里云 DashScope API Key（[申请地址](https://dashscope.aliyun.com/)）

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd career_agent_backend
2. 创建虚拟环境并安装依赖
bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

pip install -r requirements.txt
3. 配置环境变量
复制 .env.example 为 .env，并填写实际配置：

ini
# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=career_agent

# Neo4j（可选）
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password

# DashScope
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx
QWEN_MODEL=qwen-turbo   # 可选 qwen-plus

# JWT 认证
SECRET_KEY=your-secret-key-here   # 生成随机字符串，如 openssl rand -hex 32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 文件存储路径
UPLOAD_DIR=./data/uploads
REPORT_DIR=./data/reports
4. 初始化数据库
bash
python init_db.py
该脚本会删除并重建 career_agent 数据库，创建所有表。

5. 导入原始岗位数据
将岗位 Excel 文件（默认 data/jobs.xlsx）放入 data/ 目录，然后运行：

bash
python import_jobs.py
6. （可选）筛选计算机/信息技术岗位
bash
python filter_jobs.py
python filter_by_llm.py
此脚本会从 jobs 表筛选出计算机/信息技术相关的岗位，存入 jobs_computer 表。后续生成画像建议使用该表以节省时间和成本。

7. 生成岗位画像（建议先测试少量数据）
7.1 生成个体画像（每条招聘记录）
bash
python generate_job_profiles.py
该脚本会调用大模型为 jobs_computer 中的每条记录生成画像，支持断点续传。首次运行建议先测试少量数据（修改脚本中 jobs = jobs[:10]）。

7.2 聚合生成典型画像
bash
python aggregate_job_profiles.py
基于个体画像，按岗位名称聚合出典型画像，存入 job_title_profiles 表。

8. 生成区域统计信息
bash
python generate_region_stats.py
从 jobs_computer 表计算各岗位在不同区域的薪资、需求、主要城市，存入 job_region_stats 表。

9. （可选）构建岗位图谱
确保 Neo4j 服务已启动（neo4j console），然后运行：

bash
python build_job_graph.py
该脚本为每个岗位名称生成晋升和换岗路径，存入 Neo4j。建议先测试少量岗位（修改脚本中 job_titles = job_titles[:10]）。

10. 启动后端服务
bash
uvicorn app.main:app --reload
服务启动后，访问 http://localhost:8000/docs 查看交互式 API 文档。

📡 API 接口概览
模块	方法	路径	功能
认证	POST	/api/v1/auth/login	用户登录，返回 token
认证	POST	/api/v1/auth/register	用户注册
岗位	GET	/api/v1/jobs/	获取所有岗位基本信息
岗位	GET	/api/v1/jobs/{job_title}/profile	获取岗位典型画像（含区域统计）
岗位	GET	/api/v1/job-titles	获取去重后的岗位名称列表（支持搜索）
岗位	GET	/api/v1/graph/{job_name}	获取岗位图谱路径
学生	POST	/api/v1/students/upload	上传简历生成学生画像
学生	PUT	/api/v1/students/{student_id}/profile	手动更新学生信息（基本信息、经历、技能等）
学生	POST	/api/v1/students/{student_id}/finalize	确认生成完整画像
学生	GET	/api/v1/students/{student_id}	获取学生信息
学生	GET	/api/v1/students/{student_id}/versions	获取简历历史版本列表
学生	GET	/api/v1/students/{student_id}/versions/{version_id}	获取指定版本详情
学生	POST	/api/v1/students/parse-text	解析自由文本为结构化经历
匹配	GET	/api/v1/match/student/{student_id}	获取学生与所有岗位的匹配度
报告	POST	/api/v1/report/generate	求职主线：一键生成报告
报告	POST	/api/v1/report/generate_path_report	探索主线：生成规划报告
报告	POST	/api/v1/report/preview	预览报告数据（供前端编辑）
报告	POST	/api/v1/report/export	导出编辑后的报告
报告	POST	/api/v1/report/polish	润色文本
报告	GET	/api/v1/report/history	获取当前用户的历史报告列表
路径	GET	/api/v1/career-paths/recommendations	推荐职业路径
路径	POST	/api/v1/career-paths/select	选择路径并生成发展计划
路径	GET	/api/v1/career-paths/refresh	刷新匹配度，获取备选路径
详细接口说明见 API 文档（启动服务后）。

🧪 数据生成流程（可选）
如果已经提供了预处理好的 job_title_profiles、job_region_stats 和 Neo4j 图谱数据，你可以跳过步骤 7-9，直接启动服务。否则，请按上述步骤执行。

🔍 质量保证与创新点
Few-shot 提示词：在生成画像时提供示例，减少模型输出偏差。

后处理校验：对模型输出的技能、证书、能力评分进行合法性检查和标准化。

置信度自评+重试：每次生成后模型对自己的输出打分，低于阈值则自动重试（最多3次），提高输出质量。

技能标准化与模糊匹配：建立同义词库，并利用字符串相似度匹配技能，提升匹配准确率。

多维度匹配：将匹配分解为基础要求、职业技能、职业素养、发展潜力四个维度，分别计算得分，更符合实际评价标准。

雷达图可视化：在报告中直观展示四维度匹配情况。

学习资源推荐：根据学生差距，生成带链接的个性化学习资源（课程、书籍、项目）。

岗位调动建议：基于图谱路径，提供从当前岗位向其他岗位发展的具体行动指南。

用户认证与数据隔离：JWT 认证确保用户数据安全。

历史版本管理：支持回溯简历版本和报告历史。

双主线设计：求职主线与探索主线并行，满足不同阶段学生需求。

PDCA 闭环：报告中融入计划-执行-检查-调整框架，支持动态评估与优化。

❓ 常见问题
Q: 为什么启动服务后部分接口返回 500 错误？
A: 检查 .env 中的数据库密码、API Key 是否正确，并确认 MySQL/Neo4j 服务已启动。

Q: 个体画像生成太慢怎么办？
A: 可以限制每个岗位最多生成 20 条个体画像（脚本中已支持），或使用多进程并发（需谨慎，可能触发 API 限流）。

Q: 报告中的雷达图无法显示？
A: 确保已安装 matplotlib，并且系统支持中文字体（可设置 plt.rcParams['font.sans-serif'] = ['SimHei']）。

Q: 如何更新已生成的岗位画像？
A: 重新运行 generate_job_profiles.py 和 aggregate_job_profiles.py 即可（支持断点续传）。

Q: Neo4j 服务连接失败？
A: 确认 Neo4j 已启动且 bolt://localhost:7687 可访问，用户名密码正确。若无需图谱，可忽略此问题。

Q: 用户登录后如何认证？
A: 登录成功后获得 token，后续请求需在 HTTP 头中添加 Authorization: Bearer <token>。前端已在 axios 拦截器中实现。

Q: 如何查看历史简历版本？
A: 调用 GET /api/v1/students/{student_id}/versions，其中 student_id 为当前用户关联的学生 ID。每个版本包含版本号和时间戳。

Q: 报告文件名为什么是 report_{student_id}_{job_title}.docx？
A: 为了确保文件名唯一且便于权限校验，报告文件名使用学生 ID 和清理后的岗位名称。

📝 从零开始的工作总结
一、项目启动与环境搭建
技术选型：FastAPI + MySQL + Neo4j + 千问大模型

环境配置：虚拟环境、依赖安装、.env 配置

数据库初始化：init_db.py 一键创建所有表

二、数据处理与岗位画像生成
数据清洗：filter_jobs.py 关键词筛选，filter_by_llm.py 二次筛选（可选）

个体画像生成：generate_job_profiles.py 为每条招聘记录生成 13 维画像，支持断点续传和自动重试

典型画像聚合：aggregate_job_profiles.py 按岗位名称聚合，生成典型画像

区域统计：generate_region_stats.py 按四大区域统计薪资、需求、主要城市

岗位图谱：build_job_graph.py 调用大模型生成晋升/换岗路径，存入 Neo4j

三、学生画像与用户认证
用户模型：User 表，支持 JWT 认证

登录注册接口：/auth/login 和 /auth/register，返回 token

学生画像：

简历上传：解析 PDF/Word/TXT，调用大模型生成画像

手动录入：PUT /students/{id}/profile 更新基本信息、经历、技能

画像最终确认：POST /students/{id}/finalize 综合所有信息生成完整画像

历史版本管理：resume_versions 表，每次更新自动保存版本

四、人岗匹配与报告生成
匹配算法：多维度匹配（基础要求、职业技能、职业素养、发展潜力），技能模糊匹配

报告生成（求职主线）：

预览、润色、导出接口

PDCA 框架融入报告

雷达图可视化

报告生成（探索主线）：

接收前端提交的学生信息、路径、计划等，生成 PDCA 规划报告

五、职业路径推荐与动态调整
路径推荐：基于学生画像，调用大模型推荐 2-3 条路径，含名称、介绍、匹配度

路径选择：生成 PDCA 发展计划，保存到学生画像

动态刷新：重新评估匹配度，提供备选路径

六、质量保证与评估
画像生成自带置信度自评和自动重试

技能匹配同义词库+模糊匹配

评估脚本 evaluate_accuracy.py 人工抽样验证

七、接口总览与前端对接
提供完整的 RESTful API 文档（Swagger UI）

支持双主线无缝切换

📄 许可证
本项目遵循 MIT 许可证，详见 LICENSE 文件。

🙏 致谢
感谢阿里云 DashScope 提供的大模型服务，以及开源社区提供的各种优秀库。

立即开始你的职业规划之旅！ 🎉