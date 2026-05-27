#!/usr/bin/env python3
import subprocess
import re
import time
from datetime import datetime

class LLMTokenMonitor:
    def __init__(self):
        self.session_tokens = {"input": 0, "output": 0, "total": 0}
        
    def get_recent_logs(self, lines=200):
        """Fetch recent logs from AI service"""
        cmd = f"docker logs wrenai-wren-ai-service-1 --tail {lines} 2>&1"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout
    
    def parse_token_usage(self, log_content):
        """Extract token usage patterns from logs"""
        patterns = [
            r'input_tokens?[:\s=]+(\d+)',
            r'output_tokens?[:\s=]+(\d+)', 
            r'total_tokens?[:\s=]+(\d+)',
            r'prompt[:\s=]+(\d+)',
            r'completion[:\s=]+(\d+)',
            r'(\d+)\s+input\s+(\d+)\s+output',
        ]
        
        found = []
        for line in log_content.split('\n'):
            for pattern in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    found.append(line.strip())
                    break
        return found
    
    def monitor_query(self, duration=30):
        """Monitor token usage for 30 seconds"""
        print(f"\n{'='*60}")
        print(f"🔍 LLM Token Usage Monitor")
        print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
        print(f"📊 Monitoring for {duration} seconds...")
        print(f"{'='*60}\n")
        
        print("Ask a question in Wren UI now!")
        print("Waiting for LLM calls...\n")
        
        time.sleep(duration)
        
        logs = self.get_recent_logs(100)
        token_lines = self.parse_token_usage(logs)
        
        if token_lines:
            print("✅ Token usage found in logs:")
            for line in token_lines[-10:]:  # Last 10 token entries
                print(f"  {line}")
        else:
            print("⚠️ No token usage lines found in recent logs")
            print("\n💡 Try these commands manually:")
            print("  docker logs wrenai-wren-ai-service-1 --tail 200 | grep -i token")
    
    def estimate_token_cost(self, input_tokens, output_tokens):
        """Estimate cost (if using paid API)"""
        # Rough estimates for hosted Llama 3.1 8B
        input_cost = input_tokens * 0.0000002  # ~$0.20 per million tokens
        output_cost = output_tokens * 0.0000002
        total_cost = input_cost + output_cost
        
        print(f"\n💰 Estimated Cost (if using API):")
        print(f"  Input: {input_tokens} tokens → ${input_cost:.6f}")
        print(f"  Output: {output_tokens} tokens → ${output_cost:.6f}")
        print(f"  Total: ${total_cost:.6f}")
        
        return total_cost

# Run monitor
monitor = LLMTokenMonitor()
monitor.monitor_query(duration=30)

print("\n" + "="*60)
print("💡 To see token usage per query in real-time:")
print("  docker logs -f wrenai-wren-ai-service-1 2>&1 | grep --line-buffered -E 'token|input|output'")
