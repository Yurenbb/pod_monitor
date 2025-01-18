#yuren
from kubernetes import client, config, watch
import requests
import time

# 加载 K8s 配置
#config.load_kube_config()  #localconfig
config.load_incluster_config()  #cluster

v1 = client.CoreV1Api()
apps_v1 = client.AppsV1Api()  # 添加 AppsV1Api 用于监控 Deployment
batch_v1 = client.BatchV1Api()
w = watch.Watch()

# url写死
#def send_alert(message):
#    webhook_url = "############"  #webhook URL
#    requests.post(webhook_url, json={"msgtype": "text", "text": {"content": message}})

#url读取文件
# 发送告警到企业微信
def send_alert(message):
    # 从 url.txt 文件中读取 webhook URL
    with open('url.txt', 'r') as file:
        webhook_url = file.read().strip()  # 读取并去除多余的空白字符
    requests.post(webhook_url, json={"msgtype": "text", "text": {"content": message}})


# 监控所有命名空间的 Pod 创建事件
processed_pods = set()
def monitor_pods():
    for event in w.stream(v1.list_pod_for_all_namespaces):
        if event['type'] == 'ADDED':
            pod_name = event['object'].metadata.name
            namespace = event['object'].metadata.namespace
            pod_id = f"{namespace}/{pod_name}"

            if pod_id in processed_pods:
                continue  # 已处理的 Pod，跳过

            # 添加到已处理集合
            processed_pods.add(pod_id)

            # 等待 Pod 被调度并获取 Node 名称
            for _ in range(10):  # 等待最多 10 次
                pod = v1.read_namespaced_pod(pod_name, namespace)
                if pod.status.phase == "Running" and pod.spec.node_name:
                    node_name = pod.spec.node_name
                    message = f"New Pod added: {pod_name}\nNamespace: {namespace}\nNode: {node_name}"
                    send_alert(message)
                    break
                time.sleep(1)  # 每次等待 1 秒

# 监控所有命名空间的 Job 创建事件
processed_jobs = set()
def monitor_jobs():
    for event in w.stream(batch_v1.list_job_for_all_namespaces):
        if event['type'] == 'ADDED':
            job_name = event['object'].metadata.name
            namespace = event['object'].metadata.namespace
            job_id = f"{namespace}/{job_name}"

            if job_id in processed_jobs:
                continue  # 已处理的 Job，跳过

            # 添加到已处理集合
            processed_jobs.add(job_id)

            # 获取 Job 创建的 Pods 的 Node 信息
            pods = v1.list_namespaced_pod(namespace, label_selector=f"job-name={job_name}")
            running_pods = [pod for pod in pods.items if pod.status.phase == "Running"]
            node_names = [pod.spec.node_name for pod in running_pods]
            message = f"New Job added: {job_name}\nNamespace: {namespace}"
            send_alert(message)

# 监控所有命名空间的 Deployment 创建事件
processed_deployments = set()
def monitor_deployments():
    for event in w.stream(apps_v1.list_deployment_for_all_namespaces):
        if event['type'] == 'ADDED':
            deployment_name = event['object'].metadata.name
            namespace = event['object'].metadata.namespace
            deployment_id = f"{namespace}/{deployment_name}"

            if deployment_id in processed_deployments:
                continue  # 已处理的 Deployment，跳过

            # 添加到已处理集合
            processed_deployments.add(deployment_id)

            message = f"New Deployment added: {deployment_name}\nNamespace: {namespace}"
            send_alert(message)

# 启动监控
if __name__ == "__main__":
    import threading

    # 启动前等待几秒，确保 Kubernetes 状态稳定
    time.sleep(5)

    # 使用线程同时监控 Pods、Jobs 和 Deployments
    pod_thread = threading.Thread(target=monitor_pods)
    job_thread = threading.Thread(target=monitor_jobs)
    deployment_thread = threading.Thread(target=monitor_deployments)  # 新增 Deployment 监控线程

    pod_thread.start()
    job_thread.start()
    deployment_thread.start()  # 启动 Deployment 监控

    pod_thread.join()
    job_thread.join()
    deployment_thread.join()  # 等待 Deployment 监控线程结束

