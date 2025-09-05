pipeline {
    agent any
    
    parameters {
        choice(
            name: 'TEST_TYPE',
            choices: ['smoke', 'regression', 'login', 'home'],
            description: '选择测试类型'
        )
        choice(
            name: 'PLATFORM',
            choices: ['android', 'ios'],
            description: '选择测试平台'
        )
        choice(
            name: 'ENVIRONMENT',
            choices: ['test', 'staging', 'prod'],
            description: '选择测试环境'
        )
        string(
            name: 'DEVICE_NAME',
            defaultValue: '',
            description: '设备名称（可选）'
        )
        string(
            name: 'APP_PATH',
            defaultValue: '',
            description: '应用路径（可选）'
        )
        booleanParam(
            name: 'PARALLEL_EXECUTION',
            defaultValue: false,
            description: '是否并行执行测试'
        )
    }
    
    environment {
        PYTHON_VERSION = '3.9'
        TEST_ENV = "${params.ENVIRONMENT}"
        ALLURE_RESULTS = 'reports/allure_raw'
        ALLURE_REPORT = 'reports/allure_report'
    }
    
    stages {
        stage('准备环境') {
            steps {
                echo "开始准备测试环境..."
                
                // 清理工作空间
                cleanWs()
                
                // 检出代码
                checkout scm
                
                // 设置Python环境
                sh '''
                    python3 --version
                    pip3 install --upgrade pip
                    pip3 install -r requirements.txt
                '''
                
                // 安装Allure命令行工具
                sh '''
                    if ! command -v allure &> /dev/null; then
                        echo "安装Allure命令行工具..."
                        curl -o allure-2.20.1.tgz -Ls https://github.com/allure-framework/allure2/releases/download/2.20.1/allure-2.20.1.tgz
                        tar -zxf allure-2.20.1.tgz
                        sudo mv allure-2.20.1 /opt/allure
                        sudo ln -s /opt/allure/bin/allure /usr/bin/allure
                    fi
                    allure --version
                '''
                
                // 安装和配置Appium
                sh '''
                    if ! command -v appium &> /dev/null; then
                        echo "安装Appium..."
                        npm install -g appium@next
                        appium driver install uiautomator2
                    fi
                    appium --version
                '''
            }
        }
        
        stage('环境检查') {
            steps {
                echo "检查测试环境..."
                sh 'python3 run_tests.py check'
            }
        }
        
        stage('启动Appium服务器') {
            steps {
                echo "启动Appium服务器..."
                script {
                    // 在后台启动Appium服务器
                    sh 'nohup appium --relaxed-security > appium.log 2>&1 &'
                    
                    // 等待服务器启动
                    sh '''
                        echo "等待Appium服务器启动..."
                        for i in {1..30}; do
                            if curl -s http://localhost:4723/wd/hub/status > /dev/null; then
                                echo "Appium服务器启动成功"
                                break
                            fi
                            echo "等待中... ($i/30)"
                            sleep 2
                        done
                    '''
                }
            }
        }
        
        stage('执行测试') {
            steps {
                echo "执行测试: ${params.TEST_TYPE} on ${params.PLATFORM}"
                
                script {
                    def testCommand = "python3 run_tests.py ${params.TEST_TYPE}"
                    testCommand += " --platform ${params.PLATFORM}"
                    testCommand += " --env ${params.ENVIRONMENT}"
                    
                    if (params.DEVICE_NAME) {
                        testCommand += " --device '${params.DEVICE_NAME}'"
                    }
                    
                    if (params.APP_PATH) {
                        testCommand += " --app '${params.APP_PATH}'"
                    }
                    
                    if (params.PARALLEL_EXECUTION) {
                        testCommand += " --parallel 2"
                    }
                    
                    // 执行测试，即使失败也继续后续步骤
                    sh "${testCommand} || true"
                }
            }
            post {
                always {
                    // 收集测试结果
                    publishTestResults testResultsPattern: 'reports/junit/*.xml'
                }
            }
        }
        
        stage('生成测试报告') {
            steps {
                echo "生成Allure测试报告..."
                
                script {
                    // 生成Allure报告
                    allure([
                        includeProperties: false,
                        jdk: '',
                        properties: [],
                        reportBuildPolicy: 'ALWAYS',
                        results: [[path: env.ALLURE_RESULTS]]
                    ])
                }
                
                // 生成HTML报告
                sh 'python3 run_tests.py report --no-open'
            }
        }
        
        stage('归档测试结果') {
            steps {
                echo "归档测试结果..."
                
                // 归档Allure报告
                archiveArtifacts artifacts: 'reports/allure_report/**/*', allowEmptyArchive: true
                
                // 归档HTML报告
                archiveArtifacts artifacts: 'reports/html/**/*', allowEmptyArchive: true
                
                // 归档截图
                archiveArtifacts artifacts: 'reports/screenshots/**/*', allowEmptyArchive: true
                
                // 归档日志
                archiveArtifacts artifacts: 'logs/**/*', allowEmptyArchive: true
                
                // 发布HTML报告
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports/html',
                    reportFiles: 'test_report.html',
                    reportName: 'HTML测试报告'
                ])
            }
        }
    }
    
    post {
        always {
            echo "清理环境..."
            
            // 停止Appium服务器
            sh 'pkill -f appium || true'
            
            // 清理临时文件
            sh 'rm -f appium.log nohup.out'
        }
        
        success {
            echo "测试执行成功！"
            
            // 发送成功通知
            emailext (
                subject: "UI自动化测试成功 - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                测试执行成功！
                
                构建信息：
                - 任务: ${env.JOB_NAME}
                - 构建号: ${env.BUILD_NUMBER}
                - 测试类型: ${params.TEST_TYPE}
                - 测试平台: ${params.PLATFORM}
                - 测试环境: ${params.ENVIRONMENT}
                
                查看详细报告: ${env.BUILD_URL}allure
                """,
                to: "${env.CHANGE_AUTHOR_EMAIL ?: 'dev-team@company.com'}"
            )
        }
        
        failure {
            echo "测试执行失败！"
            
            // 发送失败通知
            emailext (
                subject: "UI自动化测试失败 - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                测试执行失败，请检查！
                
                构建信息：
                - 任务: ${env.JOB_NAME}
                - 构建号: ${env.BUILD_NUMBER}
                - 测试类型: ${params.TEST_TYPE}
                - 测试平台: ${params.PLATFORM}
                - 测试环境: ${params.ENVIRONMENT}
                
                查看详细报告: ${env.BUILD_URL}allure
                查看控制台输出: ${env.BUILD_URL}console
                """,
                to: "${env.CHANGE_AUTHOR_EMAIL ?: 'dev-team@company.com'}"
            )
        }
        
        unstable {
            echo "测试不稳定，存在失败的测试用例。"
        }
        
        changed {
            echo "测试结果状态发生变化。"
        }
    }
}