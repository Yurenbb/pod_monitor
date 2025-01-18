# pod_monitor
This is an alarm service for monitoring resource creation related to k8s. Currently, only resource addition alarms for deployment, pod, and job are added.
Relevant alarm information will be sent to your webhook address. Here we tested the enterprise wechat.
The effect is shown in the figure
![image](https://github.com/user-attachments/assets/e122c648-5ddd-406b-8cde-6d9d0273c4b5)

New Pod added: kube-scheduler-yuren
Namespace: kube-system
Node: yuren

New Deployment added: calico-kube-controllers
Namespace: kube-system

New Job added: 6787726244bd3eede329ccf4
Namespace: 674029a1d1c55de5624fd935

method of application：
1.Replace YOUR_WEBHOOK_URL in the configmap in the deploy.yaml file with your webhook address and # YOUR_NAMESPACE with the namespace you need to deploy.
2.kubectl apply -f deploy.yaml -n namespace

ps:
test.py is the main application file from which you can modify and add functionality, and then dockerfile rebuilds the image, replacing the image in deploy.yaml with the new image.
