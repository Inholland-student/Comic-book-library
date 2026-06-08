# =============================================================================
# RED PHASE — TDD Security Test (Intentionally Insecure — DO NOT DEPLOY)
# =============================================================================
# This file exists ONLY to demonstrate that Checkov catches critical
# misconfigurations and stops the pipeline before they reach production.
#
# Violations triggered (all CRITICAL/HIGH):
#   CKV_K8S_16  — privileged container (full host access)
#   CKV_K8S_6   — container runs as root (UID 0)
#   CKV_K8S_28  — hostNetwork exposes all host interfaces
#   CKV_K8S_30  — hostPID allows reading every host process
#   CKV_K8S_37  — allowPrivilegeEscalation enables sudo-like escalation
#   CKV_K8S_8   — no liveness probe (silent crash = hidden breach)
#   CKV_K8S_9   — no readiness probe
#   CKV_K8S_11  — no CPU limit (noisy-neighbour / DoS risk)
#   CKV_K8S_12  — no memory limit
# =============================================================================

resource "kubernetes_deployment" "insecure_demo" {
  metadata {
    name      = "insecure-demo"
    namespace = "default"
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "insecure-demo"
      }
    }

    template {
      metadata {
        labels = {
          app = "insecure-demo"
        }
      }

      spec {
        # CKV_K8S_28 — shares every host network interface (e.g. can sniff all pod traffic)
        host_network = true

        # CKV_K8S_30 — can see and kill every process on the host
        host_pid = true

        container {
          name  = "insecure-app"
          image = "ubuntu:latest"

          # No liveness probe  → CKV_K8S_8
          # No readiness probe → CKV_K8S_9
          # No resource limits → CKV_K8S_11, CKV_K8S_12

          security_context {
            # CKV_K8S_16 — full host root access, can load kernel modules, raw sockets, etc.
            privileged = true

            # CKV_K8S_6 — explicit root UID
            run_as_user = 0

            # CKV_K8S_37 — allows the process to gain more privileges than its parent
            allow_privilege_escalation = true

            # Disables all Linux seccomp/AppArmor protections
            run_as_non_root = false
          }
        }
      }
    }
  }
}
