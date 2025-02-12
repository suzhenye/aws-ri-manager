import boto3
import os
import time
import logging
from datetime import datetime, timedelta, timezone
from botocore.config import Config
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def retry_with_backoff(max_attempts=3, initial_delay=1, max_delay=10):
    def decorator(func):
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except ClientError as e:
                    if attempt == max_attempts - 1:
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed, retrying...")
                    time.sleep(min(delay, max_delay))
                    delay *= 2
        return wrapper
    return decorator

class ConfigManager:
    """从SSM Parameter Store获取配置"""
    def __init__(self):
        self.ssm = boto3.client('ssm', config=Config(region_name='cn-northwest-1'))
        
    @retry_with_backoff()
    def get_parameter(self, name):
        try:
            response = self.ssm.get_parameter(
                Name=name,
                WithDecryption=True
            )
            return response['Parameter']['Value']
        except ClientError as e:
            if e.response['Error']['Code'] == 'ParameterNotFound':
                logger.error(f"Parameter {name} not found")
            raise

# 在 NORMALIZATION_FACTORS 中添加新服务的标准化因子
NORMALIZATION_FACTORS = {
    'ec2': {
        # 添加 t2 系列
        't2.nano': 0.25,
        't2.micro': 0.5,
        't2.small': 1,
        't2.medium': 2,
        't2.large': 4,
        't2.xlarge': 8,
        't2.2xlarge': 16,
        # 现有 t3 系列
        't3.nano': 0.25,
        't3.micro': 0.5,
        't3.small': 1,
        't3.medium': 2,
        't3.large': 4,
        't3.xlarge': 8,
        't3.2xlarge': 16,
        'm5.large': 4,
        'm5.xlarge': 8,
        'm5.2xlarge': 16,
        'm5.4xlarge': 32,
        'm5.8xlarge': 64,
        'm5.12xlarge': 96,
        'm5.16xlarge': 128,
        'm5.24xlarge': 192,
        'c5.large': 4,
        'c5.xlarge': 8,
        'c5.2xlarge': 16,
        'c5.4xlarge': 32,
        'c5.9xlarge': 72,
        'c5.12xlarge': 96,
        'c5.18xlarge': 144,
        'c5.24xlarge': 192,
        'r5.large': 4,
        'r5.xlarge': 8,
        'r5.2xlarge': 16,
        'r5.4xlarge': 32,
        'r5.8xlarge': 64,
        'r5.12xlarge': 96,
        'r5.16xlarge': 128,
        'r5.24xlarge': 192
    },
    'rds': {
        # MySQL 实例
        'MYSQL.db.t3.micro': 0.5,
        'MYSQL.db.t3.small': 1,
        'MYSQL.db.t3.medium': 2,
        'MYSQL.db.t3.large': 4,
        'MYSQL.db.t3.xlarge': 8,
        'MYSQL.db.t3.2xlarge': 16,
        'MYSQL.db.m5.large': 4,
        'MYSQL.db.m5.xlarge': 8,
        'MYSQL.db.m5.2xlarge': 16,
        'MYSQL.db.m5.4xlarge': 32,
        'MYSQL.db.m5.8xlarge': 64,
        'MYSQL.db.m5.12xlarge': 96,
        'MYSQL.db.m5.16xlarge': 128,
        'MYSQL.db.m5.24xlarge': 192,
        'MYSQL.db.r5.large': 4,
        'MYSQL.db.r5.xlarge': 8,
        'MYSQL.db.r5.2xlarge': 16,
        'MYSQL.db.r5.4xlarge': 32,
        'MYSQL.db.r5.8xlarge': 64,
        'MYSQL.db.r5.12xlarge': 96,
        'MYSQL.db.r5.16xlarge': 128,
        'MYSQL.db.r5.24xlarge': 192,

        # PostgreSQL 实例
        'POSTGRESQL.db.t3.micro': 0.5,
        'POSTGRESQL.db.t3.small': 1,
        'POSTGRESQL.db.t3.medium': 2,
        'POSTGRESQL.db.t3.large': 4,
        'POSTGRESQL.db.t3.xlarge': 8,
        'POSTGRESQL.db.t3.2xlarge': 16,
        'POSTGRESQL.db.m5.large': 4,
        'POSTGRESQL.db.m5.xlarge': 8,
        'POSTGRESQL.db.m5.2xlarge': 16,
        'POSTGRESQL.db.m5.4xlarge': 32,
        'POSTGRESQL.db.m5.8xlarge': 64,
        'POSTGRESQL.db.m5.12xlarge': 96,
        'POSTGRESQL.db.m5.16xlarge': 128,
        'POSTGRESQL.db.m5.24xlarge': 192,
        'POSTGRESQL.db.r5.large': 4,
        'POSTGRESQL.db.r5.xlarge': 8,
        'POSTGRESQL.db.r5.2xlarge': 16,
        'POSTGRESQL.db.r5.4xlarge': 32,
        'POSTGRESQL.db.r5.8xlarge': 64,
        'POSTGRESQL.db.r5.12xlarge': 96,
        'POSTGRESQL.db.r5.16xlarge': 128,
        'POSTGRESQL.db.r5.24xlarge': 192,

        # MariaDB 实例
        'MARIADB.db.t3.micro': 0.5,
        'MARIADB.db.t3.small': 1,
        'MARIADB.db.t3.medium': 2,
        'MARIADB.db.t3.large': 4,
        'MARIADB.db.t3.xlarge': 8,
        'MARIADB.db.t3.2xlarge': 16,
        'MARIADB.db.m5.large': 4,
        'MARIADB.db.m5.xlarge': 8,
        'MARIADB.db.m5.2xlarge': 16,
        'MARIADB.db.m5.4xlarge': 32,
        'MARIADB.db.m5.8xlarge': 64,
        'MARIADB.db.m5.12xlarge': 96,
        'MARIADB.db.m5.16xlarge': 128,
        'MARIADB.db.m5.24xlarge': 192,
        'MARIADB.db.r5.large': 4,
        'MARIADB.db.r5.xlarge': 8,
        'MARIADB.db.r5.2xlarge': 16,
        'MARIADB.db.r5.4xlarge': 32,
        'MARIADB.db.r5.8xlarge': 64,
        'MARIADB.db.r5.12xlarge': 96,
        'MARIADB.db.r5.16xlarge': 128,
        'MARIADB.db.r5.24xlarge': 192
    },
    'elasticache': {
        # t3 系列
        'cache.t3.micro': 0.5,
        'cache.t3.small': 1,
        'cache.t3.medium': 2,
        'cache.t3.large': 4,
        'cache.t3.xlarge': 8,
        'cache.t3.2xlarge': 16,
        
        # m4 系列
        'cache.m4.large': 4,
        'cache.m4.xlarge': 8,
        'cache.m4.2xlarge': 16,
        'cache.m4.4xlarge': 32,
        'cache.m4.10xlarge': 80,
        
        # m5 系列
        'cache.m5.large': 4,
        'cache.m5.xlarge': 8,
        'cache.m5.2xlarge': 16,
        'cache.m5.4xlarge': 32,
        'cache.m5.12xlarge': 96,
        'cache.m5.24xlarge': 192,
        
        # m6g 系列
        'cache.m6g.large': 4,
        'cache.m6g.xlarge': 8,
        'cache.m6g.2xlarge': 16,
        'cache.m6g.4xlarge': 32,
        'cache.m6g.8xlarge': 64,
        'cache.m6g.12xlarge': 96,
        'cache.m6g.16xlarge': 128,
        
        # r5 系列
        'cache.r5.large': 4,
        'cache.r5.xlarge': 8,
        'cache.r5.2xlarge': 16,
        'cache.r5.4xlarge': 32,
        'cache.r5.12xlarge': 96,
        'cache.r5.24xlarge': 192,
        
        # r6g 系列
        'cache.r6g.large': 4,
        'cache.r6g.xlarge': 8,
        'cache.r6g.2xlarge': 16,
        'cache.r6g.4xlarge': 32,
        'cache.r6g.8xlarge': 64,
        'cache.r6g.12xlarge': 96,
        'cache.r6g.16xlarge': 128
    },
    
    'opensearch': {
        # t3 系列
        't3.small.search': 1,
        't3.medium.search': 2,
        
        # m6g 系列
        'm6g.large.search': 4,
        'm6g.xlarge.search': 8,
        'm6g.2xlarge.search': 16,
        'm6g.4xlarge.search': 32,
        'm6g.8xlarge.search': 64,
        'm6g.12xlarge.search': 96,
        
        # r6g 系列
        'r6g.large.search': 4,
        'r6g.xlarge.search': 8,
        'r6g.2xlarge.search': 16,
        'r6g.4xlarge.search': 32,
        'r6g.8xlarge.search': 64,
        'r6g.12xlarge.search': 96,
        
        # c6g 系列
        'c6g.large.search': 4,
        'c6g.xlarge.search': 8,
        'c6g.2xlarge.search': 16,
        'c6g.4xlarge.search': 32,
        'c6g.8xlarge.search': 64,
        'c6g.12xlarge.search': 96,
        
        # r5 系列
        'r5.large.elasticsearch': 4,
        'r5.xlarge.elasticsearch': 8,
        'r5.2xlarge.elasticsearch': 16,
        'r5.4xlarge.elasticsearch': 32,
        'r5.8xlarge.elasticsearch': 64,
        'r5.12xlarge.elasticsearch': 96,
        
        # i3 系列
        'i3.large.search': 4,
        'i3.xlarge.search': 8,
        'i3.2xlarge.search': 16,
        'i3.4xlarge.search': 32,
        'i3.8xlarge.search': 64,
        'i3.16xlarge.search': 128
    }
}

class InstanceCounter:
    def __init__(self):
        self.config = ConfigManager()
        self.clients = {
            'ec2': boto3.client('ec2'),
            'rds': boto3.client('rds'),
            'elasticache': boto3.client('elasticache'),
            'opensearch': boto3.client('es', config=Config(region_name='cn-northwest-1')),
            'sns': boto3.client('sns', config=Config(region_name='cn-northwest-1'))  # 添加 SNS 客户端
        }
        
        try:
            self.auto_purchase = self.config.get_parameter('/ri-manager/auto-purchase').lower() == 'true'
        except ClientError as e:
            if e.response['Error']['Code'] == 'ParameterNotFound':
                logger.info("Parameter /ri-manager/auto-purchase not found, using default value: false")
            else:
                logger.error(f"Failed to load config: {str(e)}")
            self.auto_purchase = False
        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}")
            self.auto_purchase = False

    @retry_with_backoff()
    def get_ec2_instances(self):
        """获取EC2实例统计（按实例类型）"""
        counts = {'running': {}, 'reserved': {}}
        
        # 运行实例 - 只统计 running 状态的实例
        paginator = self.clients['ec2'].get_paginator('describe_instances')
        for page in paginator.paginate(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]):
            for reservation in page['Reservations']:
                for instance in reservation['Instances']:
                    itype = instance['InstanceType']
                    counts['running'][itype] = counts['running'].get(itype, 0) + 1

        # 预留实例 - 只统计 active 且未过期的实例
        response = self.clients['ec2'].describe_reserved_instances(
            Filters=[{'Name': 'state', 'Values': ['active']}]
        )
        current_time = datetime.now(timezone.utc)
        for ri in response['ReservedInstances']:
            if ri['End'] > current_time:  # 检查是否过期
                itype = ri['InstanceType']
                counts['reserved'][itype] = counts['reserved'].get(itype, 0) + ri['InstanceCount']
            
        return counts

    @retry_with_backoff()
    def get_rds_instances(self):
        """获取RDS实例统计（按实例类型）"""
        counts = {'running': {}, 'reserved': {}}
        
        # 标准化数据库引擎名称的函数
        def normalize_engine_name(engine):
            engine = engine.upper()
            if engine in ['POSTGRES', 'POSTGRESQL']:
                return 'POSTGRESQL'
            return engine
        
        # 运行实例 - 只统计可用状态的实例
        instances = self.clients['rds'].describe_db_instances()
        for instance in instances['DBInstances']:
            if instance['DBInstanceStatus'] == 'available':
                itype = instance['DBInstanceClass']
                engine = normalize_engine_name(instance['Engine'])  # 使用标准化的引擎名称
                instance_count = 2 if instance.get('MultiAZ', False) else 1
                
                full_type = f"{engine}.{itype}"
                counts['running'][full_type] = counts['running'].get(full_type, 0) + instance_count

        # 预留实例 - 只统计 active 且未过期的实例
        reserved = self.clients['rds'].describe_reserved_db_instances()
        current_time = datetime.now(timezone.utc)
        for ri in reserved['ReservedDBInstances']:
            if ri['State'] == 'active' and datetime.fromtimestamp(ri['StartTime'].timestamp() + ri['Duration'], timezone.utc) > current_time:
                itype = ri['DBInstanceClass']
                engine = normalize_engine_name(ri['ProductDescription'])  # 使用标准化的引擎名称
                full_type = f"{engine}.{itype}"
                counts['reserved'][full_type] = counts['reserved'].get(full_type, 0) + ri['DBInstanceCount']
        
        return counts

    @retry_with_backoff()
    def get_elasticache_instances(self):
        """获取ElastiCache实例统计（按实例类型）"""
        counts = {'running': {}, 'reserved': {}}
        
        # 运行实例 - 只统计可用状态的实例
        paginator = self.clients['elasticache'].get_paginator('describe_cache_clusters')
        for page in paginator.paginate():
            for cluster in page['CacheClusters']:
                if cluster['CacheClusterStatus'] == 'available':  # 检查集群状态
                    itype = cluster['CacheNodeType']
                    counts['running'][itype] = counts['running'].get(itype, 0) + cluster['NumCacheNodes']

        # 预留实例 - 只统计 active 且未过期的实例
        reserved = self.clients['elasticache'].describe_reserved_cache_nodes()
        current_time = datetime.now(timezone.utc)
        for ri in reserved['ReservedCacheNodes']:
            if ri['State'] == 'active' and datetime.fromtimestamp(ri['StartTime'].timestamp() + ri['Duration'], timezone.utc) > current_time:
                itype = ri['CacheNodeType']
                counts['reserved'][itype] = counts['reserved'].get(itype, 0) + ri['CacheNodeCount']
        
        return counts

    @retry_with_backoff()
    def get_opensearch_instances(self):
        """获取OpenSearch实例统计（按实例类型）"""
        counts = {'running': {}, 'reserved': {}}
        
        try:
            # 获取所有域列表
            response = self.clients['opensearch'].list_domain_names()
            logger.info(f"Found OpenSearch domains: {response}")
            
            domain_names = [domain['DomainName'] for domain in response.get('DomainNames', [])]
            
            if domain_names:
                # 批量获取域信息
                response = self.clients['opensearch'].describe_elasticsearch_domains(
                    DomainNames=domain_names
                )
                logger.info(f"Domain details: {response}")
                
                for domain in response.get('DomainStatusList', []):
                    if domain.get('Processing') is False:  # 只统计非处理中的域
                        cluster_config = domain.get('ElasticsearchClusterConfig', {})
                        itype = cluster_config.get('InstanceType')
                        instance_count = cluster_config.get('InstanceCount', 0)
                        
                        if itype and instance_count > 0:
                            counts['running'][itype] = counts['running'].get(itype, 0) + instance_count

            # 获取预留实例信息 - 只统计 active 且未过期的实例
            reserved_response = self.clients['opensearch'].describe_reserved_elasticsearch_instances()
            logger.info(f"Reserved instances: {reserved_response}")
            current_time = datetime.now(timezone.utc)
            
            for ri in reserved_response.get('ReservedElasticsearchInstances', []):
                if (ri['State'] == 'active' and 
                    datetime.fromtimestamp(ri['StartTime'].timestamp() + ri['Duration'], timezone.utc) > current_time):
                    itype = ri['ElasticsearchInstanceType']
                    counts['reserved'][itype] = counts['reserved'].get(itype, 0) + ri['ElasticsearchInstanceCount']
                    
        except Exception as e:
            logger.error(f"Failed to get OpenSearch instances: {str(e)}")
            raise
            
        return counts

def generate_report(counter):
    """生成汇总报告"""
    report = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'services': {},
        'recommendations': []
    }
    
    try:
        # 收集各服务数据
        report['services']['ec2'] = counter.get_ec2_instances()
        report['services']['rds'] = counter.get_rds_instances()
        report['services']['elasticache'] = counter.get_elasticache_instances()
        report['services']['opensearch'] = counter.get_opensearch_instances()
        
        # 生成购买建议
        for service in ['ec2', 'rds', 'elasticache', 'opensearch']:
            data = report['services'][service]
            normalized_running = 0
            normalized_reserved = 0
            type_deficits = {}
            series_stats = {}
            
            # 首先按系列分组统计
            for itype in set(data['running'].keys()) | set(data['reserved'].keys()):
                if itype not in NORMALIZATION_FACTORS.get(service, {}):
                    logger.warning(f"Instance type {itype} not found in NORMALIZATION_FACTORS for {service}")
                    continue
                    
                factor = NORMALIZATION_FACTORS[service][itype]
                running_count = data['running'].get(itype, 0)
                reserved_count = data['reserved'].get(itype, 0)
                
                # 提取实例系列
                if service == 'rds':
                    parts = itype.split('.')
                    if len(parts) >= 4:
                        series = f"{parts[0]}.{parts[1]}.{parts[2]}"
                elif service == 'elasticache':
                    parts = itype.split('.')
                    if len(parts) >= 3:
                        series = f"{parts[0]}.{parts[1]}"
                elif service == 'opensearch':
                    series = itype.split('.')[0]
                else:
                    series = itype.split('.')[0]
                
                # 初始化系列统计
                if series not in series_stats:
                    series_stats[series] = {
                        'running_normalized': 0,
                        'reserved_normalized': 0,
                        'instances': set(),
                        'running_details': {},
                        'reserved_details': {},
                        'instance_factors': {}
                    }
                
                # 更新系列统计
                series_stats[series]['running_normalized'] += running_count * factor
                series_stats[series]['reserved_normalized'] += reserved_count * factor
                series_stats[series]['instances'].add(itype)
                series_stats[series]['instance_factors'][itype] = factor
                series_stats[series]['running_details'][itype] = {
                    'count': running_count,
                    'normalized': running_count * factor,
                    'factor': factor
                }
                series_stats[series]['reserved_details'][itype] = {
                    'count': reserved_count,
                    'normalized': reserved_count * factor,
                    'factor': factor
                }
                
                normalized_running += running_count * factor
                normalized_reserved += reserved_count * factor
            
            # 计算每个系列的缺口
            for series, stats in series_stats.items():
                series_deficit = max(0, stats['running_normalized'] - stats['reserved_normalized'])
                
                if series_deficit > 0:
                    # 获取该系列所有可用的实例类型
                    all_instance_types = set()
                    for itype in NORMALIZATION_FACTORS[service].keys():
                        if service == 'rds' and itype.startswith(series):
                            all_instance_types.add(itype)
                        elif service == 'elasticache' and itype.startswith(series):
                            all_instance_types.add(itype)
                        elif service == 'opensearch' and itype.startswith(series.split('.')[0]):
                            all_instance_types.add(itype)
                        elif itype.startswith(series):
                            all_instance_types.add(itype)
                    
                    # 按实例大小排序（从小到大）
                    sorted_instances = sorted(
                        all_instance_types,
                        key=lambda x: NORMALIZATION_FACTORS[service][x]
                    )
                    
                    # 直接使用最小规格的实例来覆盖缺口
                    smallest_type = sorted_instances[0]
                    smallest_factor = NORMALIZATION_FACTORS[service][smallest_type]
                    count = int(series_deficit / smallest_factor)
                    
                    if count > 0:
                        recommendation = {
                            'service': service,
                            'instance_type': smallest_type,
                            'deficit': count,
                            'normalized_deficit': count * smallest_factor,
                            'series': series,
                            'purchase_time': (datetime.now() + timedelta(days=3)).isoformat()
                        }
                        report['recommendations'].append(recommendation)
                        
                        # 更新类型缺口信息
                        type_deficits[smallest_type] = {
                            'running': stats['running_details'].get(smallest_type, {}).get('count', 0),
                            'reserved': stats['reserved_details'].get(smallest_type, {}).get('count', 0),
                            'deficit': count,
                            'normalized_deficit': count * smallest_factor
                        }
            
            # 更新服务级别的统计信息
            report['services'][service]['normalized'] = {
                'running': normalized_running,
                'reserved': normalized_reserved,
                'total_deficit': max(0, normalized_running - normalized_reserved),
                'type_deficits': type_deficits,
                'series_stats': {s: {'deficit': max(0, st['running_normalized'] - st['reserved_normalized'])} 
                               for s, st in series_stats.items()}
            }
        
        return report
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        raise

def lambda_handler(event, context):
    try:
        counter = InstanceCounter()
        report = generate_report(counter)
        
        # 如果有购买建议，发送 SNS 通知
        if report['recommendations']:
            message = "预留实例购买建议：\n\n"
            current_type = None
            for rec in report['recommendations']:
                if 'original_type' in rec:
                    if current_type != rec['original_type']:
                        current_type = rec['original_type']
                        message += f"\n针对 {rec['service']} {current_type} 的缺口建议：\n"
                    message += f"购买 {rec['instance_type']} {rec['deficit']} 个\n"
                else:
                    message += f"服务：{rec['service']}\n"
                    message += f"实例类型：{rec['instance_type']}\n"
                    message += f"建议购买数量：{rec['deficit']}\n"
                message += f"标准化值：{rec['normalized_deficit']}\n"
                message += "-------------------\n"
            
            counter.clients['sns'].publish(
                TopicArn='arn:aws-cn:sns:cn-northwest-1:620814909999:billing',
                Message=message,
                Subject='预留实例购买建议'
            )
        
        return {
            'statusCode': 200,
            'body': report
        }
    except Exception as e:
        logger.error(f"Lambda execution failed: {str(e)}")
        return {
            'statusCode': 500,
            'body': str(e)
        }

# IAM Role配置说明：
"""
所需IAM策略：
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "VisualEditor0",
			"Effect": "Allow",
			"Action": [
				"es:DescribeReservedElasticsearchInstanceOfferings",
				"ec2:DescribeInstances",
				"elasticache:DescribeReservedCacheNodes",
				"ssm:GetParameter",
				"es:DescribeReservedInstances",
				"rds:DescribeReservedDBInstances",
				"es:DescribeReservedElasticsearchInstances",
				"es:DescribeReservedInstanceOfferings",
				"elasticache:DescribeReservedCacheNodesOfferings",
				"es:ListDomainNames",
				"rds:DescribeDBInstances",
				"ec2:DescribeReservedInstances",
				"es:DescribeElasticsearchDomains",
				"elasticache:DescribeCacheClusters",
				"sns:Publish"
			],
			"Resource": "*"
		}
	]
}
"""
"""
需要为Lambda函数配置执行角色并附加上述策略
"""

# 参数存储配置说明：
"""
1. 在Systems Manager Parameter Store创建参数：
   - /ri-manager/auto-purchase : "true" 或 "false"
   
2. 确保IAM角色包含ssm:GetParameter权限
"""