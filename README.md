# jieliu

#### 项目介绍
暂时提供视频解析，视频下载，视频合并功能

#### 目前支持站点
https://www.viki.com


#### 软件架构
1. 解析器：用于流解析和下载地址的解析，返回对象（序列化）
2. 下载处理器：
下载器：用于各类型文件的下载功能；
处理器：用于不同文件的格式转换，桢处理等，返回对象
3. 存储器：存储下载的文件相关路径进入数据库，进行统一化管理（暂时弃用worker）
4. 中央控制器：为了不让各类功能彼此依赖，所有数据的处理有中央控制器处理（暂时只让解析器和下载器解耦）
5. 监控器，监控已下载和下载中文件，进行各文件的后续操作


#### 安装教程
浏览器支持安装：
1. 服务器安装谷歌浏览器
服务器安装谷歌浏览器:https://segmentfault.com/a/1190000007705458
2. 安装浏览器驱动，不同系统安装不同类型的驱动
谷歌驱动：http://chromedriver.storage.googleapis.com/index.html?path=2.42/
3.驱动程序使用浏览器的代码配置
https://blog.csdn.net/zsjabjj/article/details/81875491
4.配置美国机器作为代理：
https://brickyang.github.io/2017/01/14/CentOS-7-%E5%AE%89%E8%A3%85-Shadowsocks-%E5%AE%A2%E6%88%B7%E7%AB%AF/
https://www.jianshu.com/p/88bce0c42dad
美国机器：安装服务器
国内机器：安装客户端
===>使用docker打包服务器环境
docker使用
5.服务器安装redis
https://blog.csdn.net/gyshun/article/details/79297107
6.ffmpeg安装
https://www.cnblogs.com/miaosha5s/p/7670447.html
7.相关库的安装
pip install -r requirements.txt 

#### 版本依赖
浏览器版本：chrome 70.0.3538.77
驱动版本：linux243，mac243

#### 使用说明
1. xxxx
2. xxxx
3. xxxx

#### 参与贡献

1. Fork 本项目
2. 新建 Feat_xxx 分支
3. 提交代码
4. 新建 Pull Request


#### 码云特技

#### plan
1.解析器功能（流地址解析和下载地址解析）初步封装完成：
能完成基本解析并且返回正确的字幕，音频，视频地址
后续开发：
 1）解析性能处理优化--P1
 2）浏览器管理优化--P1
 3）解析地址存储（避免重新解析）--P1

2.下载器功能：
 开发中（预计这些功能下周一之前ready可用）：下载文件的断网断电续传，下载队列的优先级管理，下载队列下载状态监控--P0
后续开发：
 1）下载宽带控制--P2
 2）音频视频及其他媒体文件的合并、转码、格式转换、视频水印...等媒体文件处理功能--P2
下载器只负责进行对象的文件对象的各种操作

3.存储器功能，管理下载文件地址，统一到数据库存储（暂未开始开发，预计下周开发完成，是直接程序上传还是存储在机器等待人工上传，方案待定）--P0
后续开发：
 1）多台服务器的下载地址统一化数据库管理--P2
 
4.接口服务（后续开发）：--P2
 1）流解析接口
 2）文件下载接口

5.其余解析下载站点开发

6.监控器
监控哪些文件需要进行merge处理，以及merge的先后顺序（merge成功，删除原文件）

预计下周可以完成基本的解析-->下载-->存储，完成站点部分音视频字幕数据的下载--P0

todo:
*关于媒体文件的merge处理，文件路径，id，开辟空间大小
（监控程序，存储器写完了，通过调用监控存储器，进行合并merge操作）
使用缓存处理（需要缓存的数据处理）
*关于数据库存储，下载完成或者merge队列进行相关数据存储和记录操作，交给存储器进行处理（可选不交，留有开关）
*后续内存损耗问题需要修复
*文件服务器由白山云管理
通过一个表，统一管理所有文件对象的处理，
1.数据库设计
2.实体类设计
3.文件下载设计
4.以本地作为服务器，进行相关下载操作
解析器避免重复解析，下载器避免重复下载，
控制器发现同sv，同类型字幕，finish则不再下载
下载器发现同hash_sign文件，则不考虑下载
解析器，下载器，存储器封装并完成初步ready（11.2）--
下周：多台服务器下载地址统一化管理


#### 数据表字段
如果自用，需要自建数据库表
CREATE TABLE `download_media` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cloud_path` text COMMENT '云盘地址',
  `original_url` text COMMENT '视频来源地址',
  `download_url` text COMMENT '文件下载地址',
  `total_size` int(11) DEFAULT NULL COMMENT '文件总大小',
  `media_quality` varchar(16) DEFAULT NULL COMMENT '240p;360p;480p;',
  `episode` int(11) DEFAULT NULL COMMENT '当前集数',
  `media_name` text COMMENT '媒体文件名称',
  `absolute_path` text COMMENT '文件服务器存储地址',
  `media_type` varchar(16) DEFAULT NULL COMMENT '媒体类型（audio，video，subtitle）',
  `file_type` varchar(16) DEFAULT NULL COMMENT '文件类型（MP4，MP3，txt……）',
  `upload_status` tinyint(4) DEFAULT NULL COMMENT '上传状态：0未上传，1已成功上传',
  `hash_sign` varchar(64) NOT NULL COMMENT '对于变化的url，取自定义名称+路径，进行hash，对于不变化的url+路径，取url进行hash',
  `download_status` tinyint(4) DEFAULT NULL COMMENT '下载状态：0未完成，1已下载完成，-1正在下载',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `site` varchar(16) NOT NULL COMMENT '站点源',
  `language` varchar(16) DEFAULT NULL COMMENT '语言',
  `merged_sign` varchar(64) DEFAULT NULL COMMENT '合并文件唯一标识',
  `merged_order` tinyint(4) DEFAULT NULL COMMENT '合并文件顺序',
  `merged_status` tinyint(4) DEFAULT NULL COMMENT '合并文件状态：0未合并，1已合并完成',
  `video_url` text COMMENT '定位1部video',
  `download_path` text,
  PRIMARY KEY (`id`),
  KEY `site` (`site`),
  KEY `hash_sign` (`hash_sign`)
) ENGINE=InnoDB AUTO_INCREMENT=379 DEFAULT CHARSET=utf8
（下载器的认定标准来自下载url的hash值，或者上一层命名的hash值--对于变化的下载url来说）
字幕文件下载地址变化，导致的无法判定同类文件的问题（暂由控制器层面处理）
暂时不支持下载队列的优先级管理
暂不支持gzip压缩文件的断点续下载功能
状态监控下载进度显示问题待调整

#### hash_sign说明
下载文件唯一标志(统一对文件名称进行hash)
hash_sign获取方式：文件名获取===>get_hash_sign(file_name)
各站点文件名获取方式
viki：
字幕文件——site_get_file_name_by_download_url(original_url)_language
音视频文件，merge类型文件——get_file_name_by_download_url(download_url)
merge后的下载文件——get_file_name_by_download_url(merged_sign+'_merged')



#### 下载队列优先级管理
1.放入队列：待下载，取出来：正在下载，放回去：暂停
2.如果1个队列暂停，取优先级高的待下载队列进入下载

#### 问题点
todo：
1.谷歌浏览器的无头模式并未很好使用：需要解决多线程使用无头浏览器，既不出现内存泄漏，也不出现解析不稳定的情况
目前服务器会出现很多chrome进程，但是本地不会--done
内存泄漏可能解决方案：https://github.com/electron/electron/releases
2.对于经常变换的下载地址，不能以下载地址名称来命名文件名称，应该以获取的信息命名--done
3.解析器暂时无法使用多线程处理(多线程经常出现解析不稳定的问题，解析不出数据)


#### Version
1.0
下载处理器，存储器，解析器，中央控制器，监控器基本功能完成
1.0.1
暂停存储器功能（有线程和进程不安全的情况）--性能下调，解决稳定性问题，改成直接存储，然后进行后续操作
完成处理器媒体文件合并
1.0.2
暂时将多线程解析器改为单线程，临时解决解析不稳定问题（部分该解析的无法解析成功）；
无头浏览器暂时模式变更为url===>开启无头===>操作===>关闭无头
1.0.3
兼容经常变更地址的合并音视频解析
1.0.4
针对未下载完成文件，采用.ant后缀格式，下载完成后，改为对应原格式（仅限MP4类型大文件）:暂时完成后监控器操作
1.0.5
解析加載js，timeout時間60s===>180s
正在下载中的下载状态监控：下载进度，hash存储信息；
对于同一文件（hash），如果正在下载，不再重复加入下载队列
1.0.6
新增下载队列的状态监控，防止下载中的文件继续进入下载


Development
We would love if you can contribute to make this project better. Here's how you can do it:

Fork the project.
Commit changes or bugfixes to your repo.
Submit a pull request
Sit back and relax while our maintainers checkout your changes and approve them!

