@echo off
chcp 65001 > nul 2>&1  :: 设置命令行编码为UTF-8，解决中文乱码
cls                     :: 清屏，让界面更整洁

:: #################### 提示信息 ####################
echo ==============================================
echo          我的世界模组Jar自动打包工具
echo ==============================================
echo 🔔 注意：本批处理必须放在以下文件/文件夹的同级目录运行！
echo    assets、data、LICENSE、META-INF、pack.mcmeta、things
echo ==============================================
echo.

:: #################### 手动输入版本号 + 非空校验 ####################
set "VERSION="  :: 清空版本号变量，避免残留
set /p VERSION=请输入模组版本号（如1.0.0、beta1、2.1.0-build5）：

:: 若未输入版本号，提示并退出
if not defined VERSION (
    echo.❌ 错误：版本号不能为空！请重新运行并输入版本号。
    pause > nul
    exit /b 1
)

:: #################### 定义Jar包文件名 ####################
set "JAR_NAME=Tinkers_Useful_Items-1.20.1-%VERSION%.jar"
echo.📌 即将打包生成：%JAR_NAME%
echo.🔧 正在检查Java环境（需要jar命令）...

:: #################### 检查Java环境（必装，MC开发自带） ####################
where jar > nul 2>&1
if %errorlevel% neq 0 (
    echo.❌ 错误：未找到jar命令！请确认已配置Java环境变量（MC开发电脑一般已配置）。
    pause > nul
    exit /b 1
)
echo.✅ Java环境检查通过，开始打包...
echo.

:: #################### 核心打包命令（jar命令，打包指定文件/文件夹） ####################
:: jar cf ：c=创建Jar，f=指定Jar文件名，后面跟需要打包的所有文件/文件夹（严格对应你的列表）
jar cf "%JAR_NAME%" assets data LICENSE META-INF pack.mcmeta things

:: #################### 打包结果判断 ####################
if exist "%JAR_NAME%" (
    echo.✅ 打包成功！Jar包已生成在当前目录：
    echo   %cd%\%JAR_NAME%
) else (
    echo.❌ 打包失败！请检查文件/文件夹是否存在，或是否有读写权限。
)

:: #################### 停留窗口，方便查看结果 ####################
echo.
echo ==============================================
echo 按任意键关闭窗口...
pause > nul