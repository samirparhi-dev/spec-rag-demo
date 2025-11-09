#!/usr/bin/env python3
"""
Infrastructure as Spec - Daily Report Generator

This script generates comprehensive daily reports for the Infrastructure as Spec platform,
including system health, RAG performance metrics, MCP server status, and AI-driven insights.

The report includes:
- System health and connectivity status
- RAG knowledge base statistics
- MCP server connectivity and performance
- AI-generated insights and recommendations
- Critical alerts and remediation suggestions

Usage:
    python generate_daily_report.py [--schedule]
"""

import os
import json
import requests
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse

# Configuration
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
WEAVIATE_URL = "http://localhost:8080"
OPEN_WEBUI_URL = "http://localhost:3000"
MCP_CONFIG_PATH = Path(__file__).parent.parent.parent / "mcp-config" / "mcp.json"

class ReportGenerator:
    """Generates comprehensive daily reports for the Infrastructure as Spec platform"""

    def __init__(self):
        self.report_data = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "system_health": {},
            "rag_metrics": {},
            "mcp_status": {},
            "ai_insights": {},
            "critical_alerts": [],
            "recommendations": []
        }

    def check_system_health(self) -> Dict[str, Any]:
        """Check health of all system components"""
        health = {}

        # Check LM Studio
        try:
            response = requests.get("http://localhost:1234/v1/models", timeout=5)
            health["lm_studio"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "models_loaded": len(response.json().get("data", [])) if response.status_code == 200 else 0,
                "response_time": response.elapsed.total_seconds()
            }
        except Exception as e:
            health["lm_studio"] = {"status": "unhealthy", "error": str(e)}

        # Check Weaviate
        try:
            response = requests.get(f"{WEAVIATE_URL}/v1/meta", timeout=5)
            health["weaviate"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "version": response.json().get("version", "unknown") if response.status_code == 200 else "unknown",
                "response_time": response.elapsed.total_seconds()
            }
        except Exception as e:
            health["weaviate"] = {"status": "unhealthy", "error": str(e)}

        # Check Open WebUI
        try:
            response = requests.get(f"{OPEN_WEBUI_URL}/health", timeout=5)
            health["open_webui"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time": response.elapsed.total_seconds()
            }
        except Exception as e:
            health["open_webui"] = {"status": "unhealthy", "error": str(e)}

        return health

    def get_rag_metrics(self) -> Dict[str, Any]:
        """Get RAG knowledge base metrics"""
        metrics = {}

        try:
            # Get InfraSpec class statistics
            response = requests.get(f"{WEAVIATE_URL}/v1/schema/InfraSpec", timeout=5)
            if response.status_code == 200:
                schema_info = response.json()
                metrics["schema_status"] = "exists"
                metrics["properties"] = len(schema_info.get("properties", []))
            else:
                metrics["schema_status"] = "not_found"

            # Get object count (approximate)
            response = requests.get(f"{WEAVIATE_URL}/v1/objects", timeout=5, params={"class": "InfraSpec", "limit": 1})
            if response.status_code == 200:
                metrics["total_objects"] = len(response.json().get("objects", []))
            else:
                metrics["total_objects"] = "unknown"

        except Exception as e:
            metrics["error"] = str(e)

        return metrics

    def check_mcp_servers(self) -> Dict[str, Any]:
        """Check MCP server configurations and connectivity"""
        mcp_status = {}

        if MCP_CONFIG_PATH.exists():
            try:
                with open(MCP_CONFIG_PATH, 'r') as f:
                    mcp_config = json.load(f)

                mcp_status["config_loaded"] = True
                mcp_status["servers"] = {}

                for server_name, server_config in mcp_config.get("mcpServers", {}).items():
                    mcp_status["servers"][server_name] = {
                        "configured": True,
                        "command": server_config.get("command"),
                        "args": server_config.get("args", [])
                    }

                mcp_status["total_servers"] = len(mcp_status["servers"])

            except Exception as e:
                mcp_status["config_loaded"] = False
                mcp_status["error"] = str(e)
        else:
            mcp_status["config_loaded"] = False
            mcp_status["error"] = "MCP config file not found"

        return mcp_status

    def generate_ai_insights(self) -> Dict[str, Any]:
        """Generate AI-powered insights using LM Studio"""
        insights = {}

        try:
            # Query for system health insights
            prompt = """
            Based on the Infrastructure as Spec platform status, provide insights about:
            1. Overall system health
            2. RAG knowledge base effectiveness
            3. Potential improvements
            4. Security considerations

            Keep the response concise but informative.
            """

            payload = {
                "model": "llama-3.1-8b-instruct",  # Adjust based on your loaded model
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
                "temperature": 0.3
            }

            response = requests.post(LM_STUDIO_URL, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                insights["system_analysis"] = result["choices"][0]["message"]["content"]
            else:
                insights["system_analysis"] = f"Failed to generate insights: {response.status_code}"

        except Exception as e:
            insights["error"] = f"AI insights generation failed: {str(e)}"

        return insights

    def analyze_critical_alerts(self) -> List[str]:
        """Analyze system status and generate critical alerts"""
        alerts = []

        health = self.report_data.get("system_health", {})

        # Check LM Studio
        if health.get("lm_studio", {}).get("status") != "healthy":
            alerts.append("CRITICAL: LM Studio is not responding - embeddings and chat will fail")

        # Check Weaviate
        if health.get("weaviate", {}).get("status") != "healthy":
            alerts.append("CRITICAL: Weaviate vector database is down - RAG queries will fail")

        # Check Open WebUI
        if health.get("open_webui", {}).get("status") != "healthy":
            alerts.append("WARNING: Open WebUI interface is not accessible")

        # Check RAG metrics
        rag_metrics = self.report_data.get("rag_metrics", {})
        if rag_metrics.get("schema_status") != "exists":
            alerts.append("CRITICAL: InfraSpec schema not found in Weaviate - knowledge base not initialized")

        if rag_metrics.get("total_objects", 0) == 0:
            alerts.append("WARNING: No objects found in knowledge base - embeddings may not be loaded")

        return alerts

    def generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        health = self.report_data.get("system_health", {})
        rag_metrics = self.report_data.get("rag_metrics", {})

        # LM Studio recommendations
        lm_studio = health.get("lm_studio", {})
        if lm_studio.get("status") == "healthy":
            model_count = lm_studio.get("models_loaded", 0)
            if model_count < 2:
                recommendations.append("Load both embedding and chat models in LM Studio for full functionality")
        else:
            recommendations.append("Start LM Studio and load required models (embedding + chat)")

        # Weaviate recommendations
        if rag_metrics.get("schema_status") != "exists":
            recommendations.append("Run embedding script to initialize InfraSpec schema: cd demo_specs/scripts && python3 create_weaviate_embeddings.py")

        # Knowledge base recommendations
        total_objects = rag_metrics.get("total_objects", 0)
        if total_objects < 50:
            recommendations.append("Expand knowledge base by adding more infrastructure specifications to demo_specs/")

        # MCP recommendations
        mcp_status = self.report_data.get("mcp_status", {})
        if not mcp_status.get("config_loaded", False):
            recommendations.append("Ensure MCP configuration file exists at mcp-config/mcp.json")

        # General recommendations
        recommendations.extend([
            "Schedule daily report generation using cron: 0 9 * * * cd /path/to/repo && python3 demo_specs/scripts/generate_daily_report.py",
            "Monitor system logs regularly for early issue detection",
            "Keep LM Studio models updated for best performance",
            "Regularly backup Weaviate data and configurations"
        ])

        return recommendations

    def generate_report(self) -> str:
        """Generate the complete markdown report"""
        self.report_data["system_health"] = self.check_system_health()
        self.report_data["rag_metrics"] = self.get_rag_metrics()
        self.report_data["mcp_status"] = self.check_mcp_servers()
        self.report_data["ai_insights"] = self.generate_ai_insights()
        self.report_data["critical_alerts"] = self.analyze_critical_alerts()
        self.report_data["recommendations"] = self.generate_recommendations()

        # Generate markdown report
        report = f"""# Infrastructure as Spec - Daily Report

**Generated:** {self.report_data['timestamp']}
**Date:** {self.report_data['date']}

## 🚨 Critical Alerts

"""

        if self.report_data["critical_alerts"]:
            for alert in self.report_data["critical_alerts"]:
                report += f"- {alert}\n"
        else:
            report += "✅ No critical alerts detected\n"

        report += "\n## 📊 System Health Status\n\n"

        health = self.report_data["system_health"]
        for component, status in health.items():
            status_icon = "✅" if status.get("status") == "healthy" else "❌"
            report += f"### {component.replace('_', ' ').title()}\n"
            report += f"- **Status:** {status_icon} {status.get('status', 'unknown')}\n"

            if "models_loaded" in status:
                report += f"- **Models Loaded:** {status['models_loaded']}\n"
            if "version" in status:
                report += f"- **Version:** {status['version']}\n"
            if "response_time" in status:
                report += f"- **Response Time:** {status['response_time']:.2f}s\n"
            if "error" in status:
                report += f"- **Error:** {status['error']}\n"

            report += "\n"

        report += "## 🧠 RAG Knowledge Base Metrics\n\n"

        rag = self.report_data["rag_metrics"]
        report += f"- **Schema Status:** {'✅ Exists' if rag.get('schema_status') == 'exists' else '❌ Not Found'}\n"
        report += f"- **Total Objects:** {rag.get('total_objects', 'Unknown')}\n"
        report += f"- **Properties:** {rag.get('properties', 'Unknown')}\n"

        if "error" in rag:
            report += f"- **Error:** {rag['error']}\n"

        report += "\n## 🔗 MCP Server Status\n\n"

        mcp = self.report_data["mcp_status"]
        report += f"- **Config Loaded:** {'✅ Yes' if mcp.get('config_loaded') else '❌ No'}\n"
        report += f"- **Total Servers:** {mcp.get('total_servers', 0)}\n\n"

        if mcp.get("servers"):
            for server_name, server_info in mcp["servers"].items():
                report += f"### {server_name}\n"
                report += f"- **Configured:** ✅ Yes\n"
                report += f"- **Command:** {server_info.get('command')}\n"
                report += f"- **Args:** {' '.join(server_info.get('args', []))}\n\n"

        if "error" in mcp:
            report += f"- **Error:** {mcp['error']}\n"

        report += "## 🤖 AI-Generated Insights\n\n"

        insights = self.report_data["ai_insights"]
        if "system_analysis" in insights:
            report += insights["system_analysis"] + "\n\n"
        else:
            report += "AI insights not available\n\n"

        report += "## 💡 Recommendations\n\n"

        for rec in self.report_data["recommendations"]:
            report += f"- {rec}\n"

        report += "\n---\n\n"
        report += "*This report is generated daily to monitor the Infrastructure as Spec platform health and performance.*"

        return report

    def save_report(self, output_path: Optional[Path] = None) -> Path:
        """Save the report to a markdown file"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(f"daily_report_{timestamp}.md")

        report_content = self.generate_report()

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"📄 Report saved to: {output_path}")
        return output_path

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Generate Infrastructure as Spec daily report")
    parser.add_argument("--schedule", action="store_true", help="Run in scheduled mode (less verbose)")
    parser.add_argument("--output", type=str, help="Output file path")

    args = parser.parse_args()

    print("🚀 Infrastructure as Spec - Daily Report Generator")
    print("=" * 60)

    generator = ReportGenerator()

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = None

    try:
        saved_path = generator.save_report(output_path)

        if not args.schedule:
            print("\n✅ Report generated successfully!")
            print(f"📍 Location: {saved_path}")

            # Print critical alerts summary
            alerts = generator.report_data.get("critical_alerts", [])
            if alerts:
                print(f"\n🚨 Critical Alerts: {len(alerts)}")
                for alert in alerts[:3]:  # Show first 3
                    print(f"   - {alert}")
                if len(alerts) > 3:
                    print(f"   ... and {len(alerts) - 3} more")
            else:
                print("\n✅ No critical alerts detected")

        return 0

    except Exception as e:
        print(f"❌ Report generation failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())