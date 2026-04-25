"""Test the SSML converter with sample digest data."""

import sys
sys.path.insert(0, '/Users/rishithreddy/Documents/MorningPulse/backend')

from processor.ssml_converter import SSMLConverter

# Sample digest data
sample_digest = {
    "date": "2026-04-25",
    "competitor_updates": [
        {
            "competitor_name": "Education Advanced",
            "title": "Acquires School Software Group",
            "description": "This acquisition strengthens their K-12 market position significantly."
        },
        {
            "competitor_name": "TechLearn Inc",
            "title": "Launches AI Tutoring Platform",
            "description": "New platform uses GPT-4 for personalized student support."
        }
    ],
    "emerging_tech_trends": [
        {
            "trend": "AI-Powered Assessment",
            "explanation": "Schools are adopting automated grading systems that provide instant feedback to students."
        },
        {
            "trend": "Hybrid Learning Tools",
            "explanation": "Demand for tools that work seamlessly in both physical and virtual classrooms is growing."
        }
    ],
    "user_pain_points": [
        {
            "issue": "Integration complexity",
            "context": "Teachers report spending hours trying to connect different EdTech tools."
        },
        {
            "issue": "Data privacy concerns",
            "context": "Schools are hesitant to adopt new platforms due to FERPA compliance issues."
        }
    ]
}

def main():
    converter = SSMLConverter()
    result = converter.convert(sample_digest)
    
    print("=" * 80)
    print("SSML VERSION (for supported engines)")
    print("=" * 80)
    print(result["ssml"])
    print()
    
    print("=" * 80)
    print("PLAIN TEXT VERSION (fallback-safe)")
    print("=" * 80)
    print(result["plain_text"])
    print()
    
    print("=" * 80)
    print("VALIDATION")
    print("=" * 80)
    
    # Check SSML validity
    ssml = result["ssml"]
    has_speak_tag = ssml.startswith("<speak>") and ssml.endswith("</speak>")
    has_prosody = "<prosody" in ssml and "</prosody>" in ssml
    has_breaks = "<break" in ssml
    no_stray_tags = ssml.count("<") == ssml.count(">")
    
    print(f"✓ Has <speak> wrapper: {has_speak_tag}")
    print(f"✓ Has <prosody> tag: {has_prosody}")
    print(f"✓ Has <break> tags: {has_breaks}")
    print(f"✓ No stray tags: {no_stray_tags}")
    
    # Check plain text
    plain = result["plain_text"]
    no_tags = "<" not in plain and ">" not in plain
    has_content = len(plain) > 100
    
    print(f"✓ Plain text has no tags: {no_tags}")
    print(f"✓ Plain text has content: {has_content}")
    
    if all([has_speak_tag, has_prosody, has_breaks, no_stray_tags, no_tags, has_content]):
        print("\n✅ ALL CHECKS PASSED!")
    else:
        print("\n❌ SOME CHECKS FAILED")

if __name__ == "__main__":
    main()
