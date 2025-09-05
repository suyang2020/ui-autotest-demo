# tools/app_info_extractor.py
import subprocess
import re
import os

def get_app_info(apk_path):
    """从APK文件中提取应用信息"""
    try:
        # 使用aapt命令获取应用信息
        result = subprocess.run(
            ['aapt', 'dump', 'badging', apk_path],
            capture_output=True, text=True
        )
        
        output = result.stdout
        
        # 提取包名
        package_match = re.search(r"package: name='([^']+)'", output)
        package_name = package_match.group(1) if package_match else None
        
        # 提取启动Activity
        activity_match = re.search(r"launchable-activity: name='([^']+)'", output)
        activity_name = activity_match.group(1) if activity_match else None
        
        return {
            'app_path': os.path.abspath(apk_path),
            'appPackage': package_name,
            'appActivity': activity_name
        }
        
    except Exception as e:
        print(f"获取应用信息失败: {e}")
        return None

def get_current_activity():
    """获取当前前台Activity"""
    try:
        result = subprocess.run(
            ['adb', 'shell', 'dumpsys', 'activity', 'activities', '|', 'findstr', '"mResumedActivity"'],
            capture_output=True, text=True
        )
        
        # 从输出中提取Activity信息
        lines = result.stdout.split('\n')
        for line in lines:
            if 'mCurrentFocus' in line or 'mFocusedActivity' in line:
                # 示例: mCurrentFocus=Window{... com.example.app/com.example.app.MainActivity}
                match = re.search(r'[a-zA-Z0-9._]+/.[a-zA-Z0-9._]+', line)
                if match:
                    return match.group(0)
        return None
        
    except Exception as e:
        print(f"获取当前Activity失败: {e}")
        return None

if __name__ == "__main__":
    # 示例用法
    apk_path = input("请输入APK文件路径: ").strip()
    
    if os.path.exists(apk_path):
        info = get_app_info(apk_path)
        if info:
            print("\n应用信息:")
            print(f"应用路径: {info['app_path']}")
            print(f"包名: {info['appPackage']}")
            print(f"启动Activity: {info['appActivity']}")
    else:
        print("文件不存在，尝试获取当前运行的应用信息...")
        current_activity = get_current_activity()
        if current_activity:
            package, activity = current_activity.split('/')
            print(f"\n当前运行的应用:")
            print(f"包名: {package}")
            print(f"Activity: {activity}")