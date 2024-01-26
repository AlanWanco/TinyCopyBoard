# TinyCopyBoard
一个迷你剪贴板实时显示悬浮窗，默认置顶，双击程序缩小到托盘，右键托盘菜单可以还原窗口或者退出。
* 如果剪贴板内是文字，显示文字。（如果显示文字，双击程序边缘可以缩小）
* 如果剪贴板内是图片，显示以窗口为高度等比缩放后的图片
* 如果剪贴板内是文件，显示文件路径

## 开发缘由
虽然我有在用ditto，但经常忘了开，想要一个可以随时提示剪贴板内容的小窗口来监控。ditto如果要显示很多剪贴板历史的话，窗口会开得很大，我只想要一个存在感不大的提示小窗口。

## 特性
* 由于python机制，运行程序时会临时生成icon文件后删除
* 无法修改窗口大小
* 没有热键最小化到托盘和还原窗口
* 无法自定义外观，无法更改托盘和icon图标
* 单独exe文件
