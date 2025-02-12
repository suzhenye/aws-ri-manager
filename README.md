# aws-ri-manager
# AWS Reserved Instance Manager

A serverless application that helps manage AWS Reserved Instances (RIs) across multiple services, providing purchase recommendations based on current usage patterns.

## Features

- Monitors running instances across multiple AWS services:
  - EC2
  - RDS
  - ElastiCache
  - OpenSearch
- Tracks active Reserved Instances
- Calculates RI coverage and deficits
- Provides normalized instance size recommendations
- Sends notifications via SNS for purchase recommendations
- Supports multi-AZ deployments

## Prerequisites

- AWS Account
- Python 3.8+
- AWS CLI configured with appropriate credentials
- IAM permissions for accessing required AWS services

## Installation

1. Clone this repository:
```bash
git clone https://github.com/suzhenye/aws-ri-manager.git
cd ri-manager
2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install boto3
 ```

3. Deploy as AWS Lambda function:
   - Create a Lambda function with Python 3.8+ runtime
   - Set the execution role with required permissions
   - Upload the code
   - Configure environment variables if needed
## Configuration
1. Create SSM Parameter:
   
   - Name: /ri-manager/auto-purchase
   - Type: String
   - Value: "true" or "false"
2. Configure SNS Topic for notifications:
   
   - Create an SNS topic
   - Update the SNS topic ARN in the code
   - Subscribe to the topic to receive notifications
## IAM Permissions
Lambda functions need to add the following permissions to the standard running permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:DescribeReservedInstances",
                "rds:DescribeDBInstances",
                "rds:DescribeReservedDBInstances",
                "elasticache:DescribeCacheClusters",
                "elasticache:DescribeReservedCacheNodes",
                "es:DescribeElasticsearchDomains",
                "es:ListDomainNames",
                "es:DescribeReservedElasticsearchInstances",
                "ssm:GetParameter",
                "sns:Publish"
            ],
            "Resource": "*"
        }
    ]
}
 ```

## Usage
The application runs as a Lambda function and can be triggered by:

- CloudWatch Events/EventBridge (recommended)
- Manual invocation
- API Gateway
The function will:

1. Collect instance data from all supported services
2. Calculate current usage and RI coverage
3. Generate purchase recommendations
4. Send notifications if recommendations are available
# AWS 预留实例管理器
一个无服务器应用程序，用于管理多个 AWS 服务的预留实例（RI），基于当前使用模式提供购买建议。

## 功能特点
- 监控多个 AWS 服务的运行实例：
  - EC2
  - RDS
  - ElastiCache
  - OpenSearch
- 跟踪活跃的预留实例
- 计算预留实例覆盖率和缺口
- 提供标准化的实例规格建议
- 通过 SNS 发送购买建议通知
- 支持多可用区部署
## 前置要求
- AWS 账号
- Python 3.8+ Python 3.8+
- 配置了适当凭证的 AWS CLI
- 访问所需 AWS 服务的 IAM 权限
## 安装步骤
1. 克隆代码仓库： 克隆代码仓库：
```bashbash
git clone https://github.com/suzhenye/aws-ri-manager.git
cd ri-manager
 ```

2. 创建虚拟环境并安装依赖：
```bash
python -m venv venv
source venv/bin/activate  # Windows 系统使用: .\venv\Scripts\activate
pip install boto3
 ```

3. 部署为 AWS Lambda 函数：
   - 创建 Python 3.8+ 运行时的 Lambda 函数
   - 设置具有所需权限的执行角色
   - 上传代码
   - 根据需要配置环境变量
## 配置说明
1. 创建 SSM 参数：
   
   - 名称： /ri-manager/auto-purchase
   - 类型：String
   - 值："true" 或 "false"
2. 配置 SNS 通知：
   
   - 创建 SNS 主题
   - 更新代码中的 SNS 主题 ARN
   - 订阅主题以接收通知
## IAM 权限
Lambda 函数需要在标准运行权限的基础上，增加以下权限：

```jsonjson
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:DescribeReservedInstances",
                "rds:DescribeDBInstances",
                "rds:DescribeReservedDBInstances",
                "elasticache:DescribeCacheClusters",
                "elasticache:DescribeReservedCacheNodes",
                "es:DescribeElasticsearchDomains",
                "es:ListDomainNames",
                "es:DescribeReservedElasticsearchInstances",
                "ssm:GetParameter",
                "sns:Publish"
            ],
            "Resource": "*"
        }
    ]
}
 ```

## 使用说明
该应用程序作为 Lambda 函数运行，可以通过以下方式触发：

- CloudWatch Events/EventBridge（推荐）
- 手动调用
- API Gateway
函数将：

1. 收集所有支持服务的实例数据
2. 计算当前使用情况和预留实例覆盖率
3. 生成购买建议
4. 如有建议则发送通知

## 运行结果输出示例：

```json
Response:
{
  "statusCode": 200,
  "body": {
    "timestamp": "2025-02-12T03:30:18.315890+00:00",
    "services": {
      "ec2": {
        "running": {
          "t2.small": 1,
          "m5.large": 7,
          "t3.large": 2,
          "t3.xlarge": 6,
          "m5.2xlarge": 36,
          "m5.xlarge": 17,
          "t3.2xlarge": 67,
          "t3.medium": 2,
          "r5.2xlarge": 40,
          "t2.xlarge": 1,
          "r5.xlarge": 12,
          "m5.4xlarge": 3,
          "r5.4xlarge": 3
        },
        "reserved": {
          "t3.nano": 3386,
          "r5.large": 342,
          "t2.nano": 44,
          "t3.xlarge": 2,
          "t3.medium": 1,
          "m5.large": 234
        },
        "normalized": {
          "running": 2809,
          "reserved": 3179.5,
          "total_deficit": 0,
          "type_deficits": {
            "t3.nano": {
              "running": 0,
              "reserved": 3386,
              "deficit": 1070,
              "normalized_deficit": 267.5
            }
          },
          "series_stats": {
            "r5": {
              "deficit": 0
            },
            "t3": {
              "deficit": 267.5
            },
            "t2": {
              "deficit": 0
            },
            "m5": {
              "deficit": 0
            }
          }
        }
      },
      "rds": {
        "running": {
          "POSTGRESQL.db.m5.xlarge": 5,
          "POSTGRESQL.db.m5.large": 1,
          "POSTGRESQL.db.m5.2xlarge": 4,
          "POSTGRESQL.db.m5.4xlarge": 4,
          "POSTGRESQL.db.t3.large": 1,
          "MYSQL.db.t3.medium": 1,
          "MARIADB.db.m5.xlarge": 1
        },
        "reserved": {
          "MYSQL.db.t3.micro": 4,
          "POSTGRESQL.db.t3.micro": 8,
          "POSTGRESQL.db.m5.large": 45,
          "POSTGRESQL.db.m5.xlarge": 3,
          "POSTGRESQL.db.m5.2xlarge": 2,
          "MYSQL.db.m5.large": 2,
          "MARIADB.db.m5.large": 2
        },
        "normalized": {
          "running": 250,
          "reserved": 258,
          "total_deficit": 0,
          "type_deficits": {},
          "series_stats": {
            "POSTGRESQL.db.m5": {
              "deficit": 0
            },
            "MARIADB.db.m5": {
              "deficit": 0
            },
            "POSTGRESQL.db.t3": {
              "deficit": 0
            },
            "MYSQL.db.m5": {
              "deficit": 0
            },
            "MYSQL.db.t3": {
              "deficit": 0
            }
          }
        }
      },
      "elasticache": {
        "running": {
          "cache.t3.micro": 10,
          "cache.t3.small": 12,
          "cache.m4.large": 3
        },
        "reserved": {
          "cache.t3.medium": 4,
          "cache.m4.large": 3,
          "cache.m6g.large": 6,
          "cache.t3.micro": 16,
          "cache.t3.small": 1
        },
        "normalized": {
          "running": 29,
          "reserved": 53,
          "total_deficit": 0,
          "type_deficits": {},
          "series_stats": {
            "cache.t3": {
              "deficit": 0
            },
            "cache.m4": {
              "deficit": 0
            },
            "cache.m6g": {
              "deficit": 0
            }
          }
        }
      },
      "opensearch": {
        "running": {
          "r5.large.elasticsearch": 6
        },
        "reserved": {
          "r5.large.elasticsearch": 14
        },
        "normalized": {
          "running": 24,
          "reserved": 56,
          "total_deficit": 0,
          "type_deficits": {},
          "series_stats": {
            "r5": {
              "deficit": 0
            }
          }
        }
      }
    },
    "recommendations": {
      {
        "service": "ec2",
        "instance_type": "t3.nano",
        "deficit": 1070,
        "normalized_deficit": 267.5,
        "series": "t3",
        "purchase_time": "2025-02-15T03:30:26.884933"
      }
    }
  }
}
 ```

## 邮件示例输出

```json
预留实例购买建议：

服务：ec2
实例类型：m5.large
建议购买数量：4
标准化值：16
-------------------
```
