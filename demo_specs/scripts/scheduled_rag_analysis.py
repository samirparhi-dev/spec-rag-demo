#!/usr/bin/env python3
"""
Infrastructure as Spec - Scheduled RAG Analysis and Auto-Healing

This script performs scheduled analysis of infrastructure specifications using RAG,
generates insights, and triggers automated remediation actions based on findings.

Features:
- Scheduled RAG queries against embedded specs
- Automated issue detection and correlation
- Auto-healing via GitLab CI/CD pipelines
- CXO dashboard data generation
- Security event forecasting and trending

Usage:
    python scheduled_rag_analysis.py [--schedule] [--target payment-service]
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse
import time

# Configuration
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
WEAVIATE_URL = "http://localhost:8080"
OPEN_WEBUI_URL = "http://localhost:3000"
DEMO_SPECS_DIR = Path(__file__).parent.parent

class ScheduledRAnalyzer:
    """Performs scheduled RAG analysis and auto-healing"""

    def __init__(self, target_service: str = "payment-service"):
        self.target_service = target_service
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "service": target_service,
            "rag_queries": [],
            "insights": [],
            "auto_healing_actions": [],
            "security_trends": {},
            "forecasting": {},
            "cxo_dashboard": {}
        }

    def perform_rag_query(self, query: str, context: str = "") -> Dict[str, Any]:
        """Perform RAG query using Open WebUI API"""
        try:
            # For demo purposes, we'll simulate RAG queries
            # In production, this would use Open WebUI's API or direct Weaviate queries

            enhanced_query = f"""
            Context: {context}

            Query: {query}

            Based on the infrastructure specifications and current system state,
            provide a detailed analysis with actionable recommendations.
            """

            payload = {
                "model": "llama-3.1-8b-instruct",
                "messages": [{"role": "user", "content": enhanced_query}],
                "max_tokens": 800,
                "temperature": 0.2
            }

            response = requests.post(LM_STUDIO_URL, json=payload, timeout=60)
            if response.status_code == 200:
                result = response.json()
                analysis = result["choices"][0]["message"]["content"]

                return {
                    "query": query,
                    "timestamp": datetime.now().isoformat(),
                    "analysis": analysis,
                    "confidence": 0.85,  # Simulated confidence score
                    "sources": ["infrastructure_specs", "kubernetes_manifests", "security_policies"]
                }
            else:
                return {
                    "query": query,
                    "error": f"RAG query failed: {response.status_code}",
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            return {
                "query": query,
                "error": f"RAG query error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def analyze_system_health(self) -> Dict[str, Any]:
        """Analyze overall system health using RAG"""
        query = f"""
        Analyze the current health status of {self.target_service} by examining:
        1. Application logs and error patterns
        2. Kubernetes pod status and resource usage
        3. Network connectivity and security policies
        4. Recent configuration changes

        Identify any anomalies, performance issues, or security concerns.
        Provide specific recommendations for improvement.
        """

        return self.perform_rag_query(query, "System Health Analysis")

    def detect_security_threats(self) -> Dict[str, Any]:
        """Detect security threats using RAG analysis"""
        query = f"""
        Perform security analysis for {self.target_service}:
        1. Review vulnerability scan results
        2. Analyze CIS benchmark compliance
        3. Check network policy effectiveness
        4. Identify potential attack vectors

        Correlate findings and assess overall security posture.
        Recommend immediate security improvements.
        """

        return self.perform_rag_query(query, "Security Threat Detection")

    def forecast_security_events(self) -> Dict[str, Any]:
        """Forecast potential security events using historical data"""
        query = f"""
        Based on current system state and historical patterns for {self.target_service}:

        1. Predict potential security incidents in the next 30 days
        2. Identify trending vulnerabilities
        3. Forecast compliance drift
        4. Anticipate capacity or performance issues

        Provide risk probabilities and mitigation strategies.
        """

        return self.perform_rag_query(query, "Security Event Forecasting")

    def generate_auto_healing_actions(self, analysis_results: List[Dict]) -> List[Dict[str, Any]]:
        """Generate automated healing actions based on analysis"""
        healing_actions = []

        for result in analysis_results:
            if "error" not in result:
                analysis = result.get("analysis", "").lower()

                # Detect critical issues and generate healing actions
                if "crashloopbackoff" in analysis or "pod failure" in analysis:
                    healing_actions.append({
                        "type": "kubernetes_restart",
                        "target": self.target_service,
                        "action": "Restart failed pods",
                        "priority": "HIGH",
                        "automation": "gitlab_ci_pipeline",
                        "estimated_time": "5 minutes"
                    })

                if "vulnerability" in analysis or "cve" in analysis:
                    healing_actions.append({
                        "type": "image_update",
                        "target": self.target_service,
                        "action": "Trigger security patch deployment",
                        "priority": "CRITICAL",
                        "automation": "gitlab_ci_pipeline",
                        "estimated_time": "30 minutes"
                    })

                if "network policy" in analysis or "firewall" in analysis:
                    healing_actions.append({
                        "type": "policy_update",
                        "target": "network_policies",
                        "action": "Update and redeploy network policies",
                        "priority": "MEDIUM",
                        "automation": "kubectl_apply",
                        "estimated_time": "10 minutes"
                    })

                if "resource limit" in analysis or "memory" in analysis or "cpu" in analysis:
                    healing_actions.append({
                        "type": "resource_scaling",
                        "target": self.target_service,
                        "action": "Auto-scale resources based on usage patterns",
                        "priority": "MEDIUM",
                        "automation": "kubernetes_hpa",
                        "estimated_time": "2 minutes"
                    })

        return healing_actions

    def generate_cxo_dashboard_data(self) -> Dict[str, Any]:
        """Generate executive dashboard data"""
        dashboard = {
            "summary": {
                "overall_health_score": 75,  # Simulated
                "security_score": 68,
                "compliance_score": 72,
                "performance_score": 85
            },
            "key_metrics": {
                "active_alerts": 3,
                "critical_vulnerabilities": 1,
                "compliance_drift": 12,
                "mttr_hours": 2.5,
                "uptime_percentage": 99.7
            },
            "trends": {
                "security_incidents_30d": [2, 1, 3, 0, 1, 2, 1],
                "compliance_score_30d": [70, 72, 71, 73, 72, 74, 72],
                "performance_score_30d": [82, 85, 83, 87, 85, 88, 85]
            },
            "risk_forecast": {
                "high_risk_events_next_30d": 2,
                "predicted_downtime_hours": 0.5,
                "recommended_budget_security": 150000
            },
            "top_risks": [
                "Container vulnerabilities requiring patching",
                "CIS compliance drift in authentication controls",
                "Network policy gaps in microservice communication"
            ]
        }

        return dashboard

    def trigger_auto_healing(self, healing_actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Trigger automated healing actions"""
        triggered_actions = []

        for action in healing_actions:
            try:
                # Simulate triggering GitLab CI pipeline or kubectl commands
                # In production, this would make actual API calls

                if action["automation"] == "gitlab_ci_pipeline":
                    # Simulate triggering GitLab pipeline
                    simulated_response = {
                        "pipeline_id": f"auto_heal_{int(time.time())}",
                        "status": "triggered",
                        "url": f"https://gitlab.example.com/pipelines/{int(time.time())}"
                    }

                elif action["automation"] == "kubectl_apply":
                    # Simulate kubectl apply
                    simulated_response = {
                        "command": f"kubectl apply -f {action['target']}",
                        "status": "executed",
                        "output": "deployment updated successfully"
                    }

                elif action["automation"] == "kubernetes_hpa":
                    # Simulate HPA adjustment
                    simulated_response = {
                        "command": f"kubectl scale deployment {self.target_service}",
                        "status": "executed",
                        "output": "horizontal pod autoscaler updated"
                    }

                triggered_actions.append({
                    **action,
                    "execution_status": "triggered",
                    "execution_time": datetime.now().isoformat(),
                    "pipeline_response": simulated_response
                })

            except Exception as e:
                triggered_actions.append({
                    **action,
                    "execution_status": "failed",
                    "error": str(e),
                    "execution_time": datetime.now().isoformat()
                })

        return triggered_actions

    def run_scheduled_analysis(self) -> Dict[str, Any]:
        """Run complete scheduled analysis"""
        print(f"🔍 Running scheduled RAG analysis for {self.target_service}")

        # Perform RAG queries
        health_analysis = self.analyze_system_health()
        security_analysis = self.detect_security_threats()
        forecast_analysis = self.forecast_security_events()

        rag_results = [health_analysis, security_analysis, forecast_analysis]

        # Generate auto-healing actions
        healing_actions = self.generate_auto_healing_actions(rag_results)

        # Trigger auto-healing (in demo mode, just simulate)
        triggered_actions = self.trigger_auto_healing(healing_actions)

        # Generate CXO dashboard data
        cxo_data = self.generate_cxo_dashboard_data()

        # Compile results
        self.analysis_results.update({
            "rag_queries": rag_results,
            "auto_healing_actions": triggered_actions,
            "cxo_dashboard": cxo_data,
            "summary": {
                "total_queries": len(rag_results),
                "successful_queries": len([r for r in rag_results if "error" not in r]),
                "healing_actions_triggered": len(triggered_actions),
                "critical_findings": len([r for r in rag_results if "CRITICAL" in str(r.get("analysis", ""))])
            }
        })

        return self.analysis_results

    def save_analysis_report(self, output_path: Optional[Path] = None) -> Path:
        """Save the analysis report"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(f"scheduled_analysis_{self.target_service}_{timestamp}.json")

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)

        print(f"📄 Analysis report saved to: {output_path}")
        return output_path

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Run scheduled RAG analysis and auto-healing")
    parser.add_argument("--schedule", action="store_true", help="Run in scheduled mode")
    parser.add_argument("--target", default="payment-service", help="Target service for analysis")
    parser.add_argument("--output", help="Output file path")

    args = parser.parse_args()

    print("🤖 Infrastructure as Spec - Scheduled RAG Analysis")
    print("=" * 60)

    analyzer = ScheduledRAnalyzer(args.target)

    try:
        results = analyzer.run_scheduled_analysis()

        if args.output:
            output_path = Path(args.output)
        else:
            output_path = None

        saved_path = analyzer.save_analysis_report(output_path)

        if not args.schedule:
            print("\n✅ Scheduled analysis completed!")
            print(f"📍 Report: {saved_path}")

            summary = results.get("summary", {})
            print(f"🔍 RAG Queries: {summary.get('total_queries', 0)}")
            print(f"✅ Successful: {summary.get('successful_queries', 0)}")
            print(f"🔧 Healing Actions: {summary.get('healing_actions_triggered', 0)}")
            print(f"🚨 Critical Findings: {summary.get('critical_findings', 0)}")

            # Print CXO dashboard summary
            cxo = results.get("cxo_dashboard", {}).get("summary", {})
            print("\n📊 CXO Dashboard:")
            print(f"   Health Score: {cxo.get('overall_health_score', 'N/A')}/100")
            print(f"   Security Score: {cxo.get('security_score', 'N/A')}/100")
            print(f"   Active Alerts: {cxo.get('active_alerts', 'N/A')}")

        return 0

    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())