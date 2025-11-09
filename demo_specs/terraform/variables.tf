variable "kubeconfig_path" {
  description = "Path to kubeconfig for terraform k8s provider"
  type        = string
  default     = "~/.kube/config"
}
