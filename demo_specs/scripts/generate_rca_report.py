#!/usr/bin/env python3
"""
Infrastructure as Spec - Root Cause Analysis (RCA) Report Generator

This script performs comprehensive Root Cause Analysis by correlating multiple security
and compliance data sources to provide actionable insights and remediation recommendations.

The RCA process analyzes:
- CIS Benchmark compliance failures
- Container vulnerabilities (Trivy)
- SBOM dependencies and licenses
- Network policies and configurations
- Application logs and events
- Kubernetes cluster state

Usage:
    python generate_rca_report.py [--target payment-service] [--format pci-dss|3ds|sox]
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse

# Configuration
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
WEAVIATE_URL = "http://localhost:8080"
DEMO_SPECS_DIR = Path(__file__).parent.parent

class RCAAnalyzer:
    """Performs comprehensive Root Cause Analysis across multiple security domains"""

    def __init__(self, target_service: str = "payment-service"):
        self.target_service = target_service
        self.findings = {
            "vulnerabilities": [],
            "compliance_failures": [],
            "misconfigurations": [],
            "dependencies": [],
            "network_issues": [],
            "application_errors": []
        }
        self.correlations = []
        self.risk_assessment = {}
        self.remediation_plan = {}

    def load_security_data(self) -> Dict[str, Any]:
        """Load all security-related data sources"""
        data = {}

        # Load CIS Benchmark Report
        cis_path = DEMO_SPECS_DIR / "security" / "cis_benchmark_report.json"
        if cis_path.exists():
            with open(cis_path, 'r') as f:
                data['cis'] = json.load(f)

        # Load Trivy Vulnerability Report
        trivy_path = DEMO_SPECS_DIR / "security" / "trivy_vulnerability_report.json"
        if trivy_path.exists():
            with open(trivy_path, 'r') as f:
                data['trivy'] = json.load(f)

        # Load SBOM Report
        sbom_path = DEMO_SPECS_DIR / "security" / "sbom_report.json"
        if sbom_path.exists():
            with open(sbom_path, 'r') as f:
                data['sbom'] = json.load(f)

        # Load network policies
        network_policies = DEMO_SPECS_DIR / "policies"
        data['policies'] = []
        for policy_file in network_policies.glob("*.yaml"):
            with open(policy_file, 'r') as f:
                data['policies'].append({
                    'filename': policy_file.name,
                    'content': f.read()
                })

        # Load application logs
        logs_dir = DEMO_SPECS_DIR / "logs"
        data['logs'] = []
        for log_file in logs_dir.glob("*.log"):
            with open(log_file, 'r') as f:
                data['logs'].append({
                    'filename': log_file.name,
                    'content': f.read()
                })

        return data

    def analyze_vulnerabilities(self, data: Dict[str, Any]) -> None:
        """Analyze container vulnerabilities"""
        if 'trivy' in data:
            trivy = data['trivy']['report']
            for vuln in trivy.get('findings', []):
                if vuln['severity'] in ['CRITICAL', 'HIGH']:
                    self.findings['vulnerabilities'].append({
                        'id': vuln['vulnerability_id'],
                        'package': vuln['package_name'],
                        'severity': vuln['severity'],
                        'cvss_score': vuln.get('cvss_score', 0),
                        'description': vuln['description'],
                        'impact': 'Container security vulnerability'
                    })

    def analyze_compliance_failures(self, data: Dict[str, Any]) -> None:
        """Analyze CIS benchmark compliance failures"""
        if 'cis' in data:
            cis = data['cis']['report']
            for failure in cis.get('failed_checks_details', []):
                if failure['severity'] in ['critical', 'high']:
                    self.findings['compliance_failures'].append({
                        'id': failure['id'],
                        'description': failure['description'],
                        'severity': failure['severity'],
                        'remediation': failure['remediation'],
                        'impact': 'Kubernetes security compliance violation'
                    })

    def analyze_misconfigurations(self, data: Dict[str, Any]) -> None:
        """Analyze configuration issues"""
        # Check for root user in containers
        if 'trivy' in data:
            trivy = data['trivy']['report']
            for misconfig in trivy.get('misconfigurations', []):
                if misconfig['severity'] == 'HIGH':
                    self.findings['misconfigurations'].append({
                        'type': 'container_misconfiguration',
                        'title': misconfig['title'],
                        'severity': misconfig['severity'],
                        'message': misconfig['message'],
                        'resolution': misconfig['resolution']
                    })

        # Check network policies
        for policy in data.get('policies', []):
            if 'payment-service' in policy['filename']:
                # Analyze policy content for potential issues
                if 'allow' in policy['content'].lower() and 'any' in policy['content'].lower():
                    self.findings['misconfigurations'].append({
                        'type': 'network_policy',
                        'title': 'Overly permissive network policy',
                        'severity': 'HIGH',
                        'message': 'Network policy allows traffic from any source',
                        'resolution': 'Restrict network policies to specific namespaces/services'
                    })

    def analyze_dependencies(self, data: Dict[str, Any]) -> None:
        """Analyze SBOM dependencies and licenses"""
        if 'sbom' in data:
            sbom = data['sbom']
            for package in sbom.get('packages', []):
                # Check for vulnerable packages
                for vuln in sbom.get('vulnerabilities', []):
                    if package['SPDXID'] in vuln.get('affectedPackages', []):
                        self.findings['dependencies'].append({
                            'package': package['name'],
                            'version': package.get('versionInfo', 'unknown'),
                            'vulnerability': vuln['name'],
                            'severity': vuln['severity'],
                            'license': package.get('licenseConcluded', 'unknown')
                        })

    def analyze_logs_and_events(self, data: Dict[str, Any]) -> None:
        """Analyze application logs and Kubernetes events"""
        for log_entry in data.get('logs', []):
            content = log_entry['content']

            # Look for specific error patterns
            if '405' in content and 'method not allowed' in content.lower():
                self.findings['application_errors'].append({
                    'type': 'http_error',
                    'code': '405',
                    'message': 'Method Not Allowed error detected',
                    'source': log_entry['filename'],
                    'impact': 'API authentication/authorization issue'
                })

            if 'crashloopbackoff' in content.lower():
                self.findings['application_errors'].append({
                    'type': 'pod_failure',
                    'status': 'CrashLoopBackOff',
                    'message': 'Pod repeatedly crashing',
                    'source': log_entry['filename'],
                    'impact': 'Application stability issue'
                })

    def correlate_findings(self) -> None:
        """Correlate findings across different domains"""
        correlations = []

        # Correlate vulnerabilities with dependencies
        vuln_packages = {f['package'] for f in self.findings['vulnerabilities']}
        dep_packages = {f['package'] for f in self.findings['dependencies']}

        if vuln_packages & dep_packages:
            correlations.append({
                'type': 'vulnerability_dependency_link',
                'description': f'Vulnerable packages found in SBOM: {vuln_packages & dep_packages}',
                'impact': 'Direct security vulnerability in application dependencies'
            })

        # Correlate compliance failures with misconfigurations
        if self.findings['compliance_failures'] and self.findings['misconfigurations']:
            correlations.append({
                'type': 'compliance_config_link',
                'description': 'CIS compliance failures related to container and network misconfigurations',
                'impact': 'Infrastructure security posture compromised'
            })

        # Correlate application errors with network policies
        if self.findings['application_errors'] and self.findings['misconfigurations']:
            network_issues = [f for f in self.findings['misconfigurations'] if f['type'] == 'network_policy']
            if network_issues:
                correlations.append({
                    'type': 'network_error_link',
                    'description': 'Application errors potentially caused by restrictive network policies',
                    'impact': 'Service availability affected by security controls'
                })

        self.correlations = correlations

    def assess_risk(self) -> Dict[str, Any]:
        """Perform comprehensive risk assessment"""
        risk_score = 0
        risk_factors = []

        # Calculate risk based on findings
        for vuln in self.findings['vulnerabilities']:
            if vuln['severity'] == 'CRITICAL':
                risk_score += 10
                risk_factors.append(f"Critical vulnerability: {vuln['id']}")
            elif vuln['severity'] == 'HIGH':
                risk_score += 5
                risk_factors.append(f"High vulnerability: {vuln['id']}")

        for compliance in self.findings['compliance_failures']:
            if compliance['severity'] == 'critical':
                risk_score += 8
                risk_factors.append(f"Critical compliance failure: {compliance['id']}")
            elif compliance['severity'] == 'high':
                risk_score += 4
                risk_factors.append(f"High compliance failure: {compliance['id']}")

        for misconfig in self.findings['misconfigurations']:
            if misconfig['severity'] == 'HIGH':
                risk_score += 6
                risk_factors.append(f"High misconfiguration: {misconfig['title']}")

        # Determine risk level
        if risk_score >= 20:
            risk_level = "CRITICAL"
        elif risk_score >= 10:
            risk_level = "HIGH"
        elif risk_score >= 5:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            'overall_risk_level': risk_level,
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'affected_components': list(set([
                self.target_service,
                'kubernetes-cluster',
                'network-infrastructure',
                'container-runtime'
            ]))
        }

    def generate_remediation_plan(self) -> Dict[str, Any]:
        """Generate comprehensive remediation plan"""
        plan = {
            'immediate_actions': [],
            'short_term_fixes': [],
            'long_term_improvements': [],
            'monitoring_recommendations': []
        }

        # Immediate actions (critical/high priority)
        for vuln in self.findings['vulnerabilities']:
            if vuln['severity'] in ['CRITICAL', 'HIGH']:
                plan['immediate_actions'].append({
                    'action': f'Update {vuln["package"]} to fix {vuln["id"]}',
                    'priority': 'CRITICAL',
                    'estimated_time': '2-4 hours',
                    'owner': 'DevSecOps Team'
                })

        for compliance in self.findings['compliance_failures']:
            if compliance['severity'] in ['critical', 'high']:
                plan['immediate_actions'].append({
                    'action': compliance['remediation'],
                    'priority': 'HIGH',
                    'estimated_time': '1-2 hours',
                    'owner': 'Platform Team'
                })

        # Short-term fixes
        for misconfig in self.findings['misconfigurations']:
            plan['short_term_fixes'].append({
                'action': misconfig['resolution'],
                'priority': 'MEDIUM',
                'estimated_time': '4-8 hours',
                'owner': 'Development Team'
            })

        # Long-term improvements
        plan['long_term_improvements'] = [
            {
                'action': 'Implement automated vulnerability scanning in CI/CD pipeline',
                'priority': 'MEDIUM',
                'estimated_time': '1-2 weeks',
                'owner': 'DevSecOps Team'
            },
            {
                'action': 'Establish CIS benchmark compliance monitoring',
                'priority': 'MEDIUM',
                'estimated_time': '1 week',
                'owner': 'Platform Team'
            },
            {
                'action': 'Implement SBOM generation and analysis in build process',
                'priority': 'LOW',
                'estimated_time': '2-3 weeks',
                'owner': 'Development Team'
            }
        ]

        # Monitoring recommendations
        plan['monitoring_recommendations'] = [
            'Implement continuous vulnerability scanning',
            'Set up CIS compliance monitoring alerts',
            'Monitor network policy violations',
            'Track application error rates and patterns',
            'Regular SBOM analysis and dependency updates'
        ]

        return plan

    def generate_ai_analysis(self) -> str:
        """Generate AI-powered analysis using LM Studio"""
        try:
            # Prepare context for AI analysis
            context = f"""
            Analyze the following security findings for {self.target_service}:

            Vulnerabilities: {len(self.findings['vulnerabilities'])}
            Compliance Failures: {len(self.findings['compliance_failures'])}
            Misconfigurations: {len(self.findings['misconfigurations'])}
            Dependency Issues: {len(self.findings['dependencies'])}

            Key Issues:
            - Critical/High Vulnerabilities: {[v['id'] for v in self.findings['vulnerabilities'] if v['severity'] in ['CRITICAL', 'HIGH']]}
            - Compliance Violations: {[c['id'] for c in self.findings['compliance_failures'] if c['severity'] in ['critical', 'high']]}
            - Network/Policy Issues: {[m['title'] for m in self.findings['misconfigurations'] if m['severity'] == 'HIGH']}

            Provide a comprehensive root cause analysis linking these issues and their business impact.
            """

            payload = {
                "model": "llama-3.1-8b-instruct",
                "messages": [{"role": "user", "content": context}],
                "max_tokens": 1000,
                "temperature": 0.3
            }

            response = requests.post(LM_STUDIO_URL, json=payload, timeout=60)
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"AI analysis failed: {response.status_code}"

        except Exception as e:
            return f"AI analysis error: {str(e)}"

    def generate_report(self, format_type: str = "comprehensive") -> str:
        """Generate the complete RCA report"""
        # Load and analyze all data
        data = self.load_security_data()

        self.analyze_vulnerabilities(data)
        self.analyze_compliance_failures(data)
        self.analyze_misconfigurations(data)
        self.analyze_dependencies(data)
        self.analyze_logs_and_events(data)
        self.correlate_findings()

        self.risk_assessment = self.assess_risk()
        self.remediation_plan = self.generate_remediation_plan()
        ai_analysis = self.generate_ai_analysis()

        # Generate report based on format
        if format_type == "pci-dss":
            return self.generate_pci_dss_report(ai_analysis)
        elif format_type == "3ds":
            return self.generate_3ds_report(ai_analysis)
        elif format_type == "sox":
            return self.generate_sox_report(ai_analysis)
        else:
            return self.generate_comprehensive_report(ai_analysis)

    def generate_comprehensive_report(self, ai_analysis: str) -> str:
        """Generate comprehensive RCA report"""
        report = f"""# Root Cause Analysis Report - {self.target_service}

**Generated:** {datetime.now().isoformat()}
**Target Service:** {self.target_service}
**Analysis Period:** Last 24 hours

## Executive Summary

This report provides a comprehensive Root Cause Analysis (RCA) of security, compliance, and operational issues affecting {self.target_service}. The analysis correlates data from multiple sources including vulnerability scans, compliance benchmarks, configuration audits, and application logs.

**Overall Risk Level:** {self.risk_assessment['overall_risk_level']}
**Risk Score:** {self.risk_assessment['risk_score']}/100

## Findings Summary

| Category | Critical | High | Medium | Total |
|----------|----------|------|--------|-------|
| Vulnerabilities | {len([v for v in self.findings['vulnerabilities'] if v['severity'] == 'CRITICAL'])} | {len([v for v in self.findings['vulnerabilities'] if v['severity'] == 'HIGH'])} | {len([v for v in self.findings['vulnerabilities'] if v['severity'] == 'MEDIUM'])} | {len(self.findings['vulnerabilities'])} |
| Compliance | {len([c for c in self.findings['compliance_failures'] if c['severity'] == 'critical'])} | {len([c for c in self.findings['compliance_failures'] if c['severity'] == 'high'])} | {len([c for c in self.findings['compliance_failures'] if c['severity'] == 'medium'])} | {len(self.findings['compliance_failures'])} |
| Misconfigurations | 0 | {len([m for m in self.findings['misconfigurations'] if m['severity'] == 'HIGH'])} | {len([m for m in self.findings['misconfigurations'] if m['severity'] == 'MEDIUM'])} | {len(self.findings['misconfigurations'])} |

## Detailed Findings

### 🔴 Critical Vulnerabilities

"""
        for vuln in self.findings['vulnerabilities']:
            if vuln['severity'] == 'CRITICAL':
                report += f"""#### {vuln['id']} - {vuln['package']}
- **Severity:** {vuln['severity']}
- **CVSS Score:** {vuln.get('cvss_score', 'N/A')}
- **Description:** {vuln['description']}
- **Impact:** {vuln['impact']}

"""

        report += """### 🟠 High Vulnerabilities

"""
        for vuln in self.findings['vulnerabilities']:
            if vuln['severity'] == 'HIGH':
                report += f"""#### {vuln['id']} - {vuln['package']}
- **Severity:** {vuln['severity']}
- **CVSS Score:** {vuln.get('cvss_score', 'N/A')}
- **Description:** {vuln['description']}
- **Impact:** {vuln['impact']}

"""

        report += """### 🔵 Compliance Failures

"""
        for compliance in self.findings['compliance_failures']:
            report += f"""#### {compliance['id']}
- **Severity:** {compliance['severity'].upper()}
- **Description:** {compliance['description']}
- **Remediation:** {compliance['remediation']}
- **Impact:** {compliance['impact']}

"""

        report += """### 🟡 Misconfigurations

"""
        for misconfig in self.findings['misconfigurations']:
            report += f"""#### {misconfig['title']}
- **Type:** {misconfig['type']}
- **Severity:** {misconfig['severity']}
- **Issue:** {misconfig['message']}
- **Resolution:** {misconfig['resolution']}

"""

        report += """## Correlation Analysis

"""
        for correlation in self.correlations:
            report += f"""### {correlation['type'].replace('_', ' ').title()}
- **Description:** {correlation['description']}
- **Business Impact:** {correlation['impact']}

"""

        report += f"""## AI-Powered Analysis

{ai_analysis}

## Risk Assessment

### Risk Level: {self.risk_assessment['overall_risk_level']}
### Risk Score: {self.risk_assessment['risk_score']}/100

### Risk Factors:
"""
        for factor in self.risk_assessment['risk_factors']:
            report += f"- {factor}\n"

        report += f"""
### Affected Components:
"""
        for component in self.risk_assessment['affected_components']:
            report += f"- {component}\n"

        report += """
## Remediation Plan

### 🚨 Immediate Actions (Execute within 24 hours)

"""
        for action in self.remediation_plan['immediate_actions']:
            report += f"""#### {action['action']}
- **Priority:** {action['priority']}
- **Estimated Time:** {action['estimated_time']}
- **Owner:** {action['owner']}

"""

        report += """
### 📅 Short-term Fixes (Execute within 1 week)

"""
        for fix in self.remediation_plan['short_term_fixes']:
            report += f"""#### {fix['action']}
- **Priority:** {fix['priority']}
- **Estimated Time:** {fix['estimated_time']}
- **Owner:** {fix['owner']}

"""

        report += """
### 🏗️ Long-term Improvements (Execute within 1 month)

"""
        for improvement in self.remediation_plan['long_term_improvements']:
            report += f"""#### {improvement['action']}
- **Priority:** {improvement['priority']}
- **Estimated Time:** {improvement['estimated_time']}
- **Owner:** {improvement['owner']}

"""

        report += """
## Monitoring Recommendations

"""
        for rec in self.remediation_plan['monitoring_recommendations']:
            report += f"- {rec}\n"

        report += """
## Compliance Mapping

### PCI DSS Requirements
- **Requirement 6.1:** Develop and maintain secure systems and applications
- **Requirement 6.2:** Ensure systems are protected from known vulnerabilities
- **Requirement 11.2.3:** Regular external vulnerability scans

### 3DS Security Requirements
- **Requirement 3.1.1:** Secure development and maintenance processes
- **Requirement 3.2.1:** Vulnerability management program
- **Requirement 3.5.1:** Secure software development lifecycle

### SOX Compliance
- **Section 404:** Internal controls over financial reporting
- **Risk Assessment:** Identification and analysis of relevant risks
- **Control Activities:** Policies and procedures for risk mitigation

## Conclusion

This RCA has identified {len(self.findings['vulnerabilities'])} vulnerabilities, {len(self.findings['compliance_failures'])} compliance failures, and {len(self.findings['misconfigurations'])} misconfigurations affecting {self.target_service}. The correlated analysis shows interconnected security issues that require immediate attention.

**Recommended Next Steps:**
1. Execute immediate remediation actions
2. Implement automated scanning and monitoring
3. Establish regular security assessments
4. Review and update security policies and procedures

---

*This report was generated automatically by the Infrastructure as Spec platform.*
*For questions or additional analysis, contact the DevSecOps team.*
"""

        return report

    def generate_pci_dss_report(self, ai_analysis: str) -> str:
        """Generate PCI DSS compliant RCA report"""
        # Similar structure but focused on PCI DSS requirements
        return self.generate_comprehensive_report(ai_analysis).replace(
            "Root Cause Analysis Report",
            "PCI DSS Compliance RCA Report"
        )

    def generate_3ds_report(self, ai_analysis: str) -> str:
        """Generate 3DS security compliant RCA report"""
        return self.generate_comprehensive_report(ai_analysis).replace(
            "Root Cause Analysis Report",
            "3DS Security RCA Report"
        )

    def generate_sox_report(self, ai_analysis: str) -> str:
        """Generate SOX compliant RCA report"""
        return self.generate_comprehensive_report(ai_analysis).replace(
            "Root Cause Analysis Report",
            "SOX Compliance RCA Report"
        )

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Generate Root Cause Analysis report")
    parser.add_argument("--target", default="payment-service", help="Target service for analysis")
    parser.add_argument("--format", choices=["comprehensive", "pci-dss", "3ds", "sox"],
                       default="comprehensive", help="Report format")
    parser.add_argument("--output", help="Output file path")

    args = parser.parse_args()

    print("🔍 Infrastructure as Spec - RCA Report Generator")
    print("=" * 60)
    print(f"Target Service: {args.target}")
    print(f"Report Format: {args.format}")

    analyzer = RCAAnalyzer(args.target)
    report_content = analyzer.generate_report(args.format)

    if args.output:
        output_path = Path(args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(f"rca_report_{args.target}_{args.format}_{timestamp}.md")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)

    print(f"✅ RCA Report generated successfully!")
    print(f"📍 Location: {output_path}")
    print(f"📊 Findings: {sum(len(v) for v in analyzer.findings.values())} total issues identified")
    print(f"🎯 Risk Level: {analyzer.risk_assessment.get('overall_risk_level', 'Unknown')}")

    return 0

if __name__ == "__main__":
    exit(main())