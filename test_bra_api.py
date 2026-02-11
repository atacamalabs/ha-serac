#!/usr/bin/env python3
"""Test script for BRA API client.

Usage:
    python test_bra_api.py <api_key> [massif_id]

Example:
    python test_bra_api.py your_api_key_here
    python test_bra_api.py your_api_key_here VANOISE
"""
import asyncio
import sys
from pathlib import Path

# Add custom_components to path
sys.path.insert(0, str(Path(__file__).parent / "custom_components" / "better_mountain_weather"))

from api.bra_client import BraClient, BraApiError


async def test_bra_api(api_key: str, massif_id: str = "CHABLAIS"):
    """Test BRA API authentication and data retrieval.

    Args:
        api_key: Météo-France API key
        massif_id: Massif identifier (default: CHABLAIS for user's location)
    """
    print("=" * 80)
    print("BRA API Test Script")
    print("=" * 80)
    print(f"\nTesting with massif: {massif_id}")
    print(f"API Key: {api_key[:8]}..." if len(api_key) > 8 else f"API Key: {api_key}")
    print()

    # Initialize client
    client = BraClient(
        api_key=api_key,
        massif_id=massif_id,
    )

    # Test bulletin retrieval
    print("-" * 80)
    print("Step 1: Fetching Avalanche Bulletin")
    print("-" * 80)
    try:
        bulletin = await client.async_get_bulletin()
        print(f"✓ Bulletin retrieved successfully")
        print()

        # Display parsed data
        print("-" * 80)
        print("Step 2: Parsed Bulletin Data")
        print("-" * 80)
        print(f"Bulletin Date: {bulletin.get('bulletin_date')}")
        print(f"Has Data: {bulletin.get('has_data')}")

        if bulletin.get('has_data'):
            print(f"\nRisk Levels:")
            print(f"  Max Risk Today: {bulletin.get('risk_max')} (1=Low, 5=Very High)")
            print(f"  Max Risk Tomorrow (J+2): {bulletin.get('risk_max_j2')}")

            print(f"\nDescriptions:")
            print(f"  Accidental Risk: {bulletin.get('accidental_text', 'N/A')[:100]}...")
            print(f"  Natural Risk: {bulletin.get('natural_text', 'N/A')[:100]}...")
            print(f"  Summary: {bulletin.get('summary', 'N/A')[:100]}...")

            altitude_risks = bulletin.get('altitude_risks', [])
            if altitude_risks:
                print(f"\nAltitude Risk Zones ({len(altitude_risks)} zones):")
                for i, zone in enumerate(altitude_risks, 1):
                    print(f"  Zone {i}: Altitude={zone.get('altitude')}, Risk={zone.get('risk')}")
        else:
            print("  No bulletin data available for this date/massif")

        print()

        # Display raw XML excerpt
        print("-" * 80)
        print("Step 3: Raw XML Response (first 500 chars)")
        print("-" * 80)
        raw_xml = bulletin.get('raw_xml', '')
        print(raw_xml[:500] + "..." if len(raw_xml) > 500 else raw_xml)
        print()

        # Save full XML to file
        output_file = Path(__file__).parent / f"bra_bulletin_{massif_id}.xml"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(raw_xml)
        print(f"✓ Full XML saved to: {output_file}")
        print()

        # Summary
        print("=" * 80)
        print("Test Summary")
        print("=" * 80)
        print("✓ API Connection: PASSED")
        print("✓ Bulletin Retrieval: PASSED")
        print("✓ XML Parsing: PASSED")

        if bulletin.get('has_data'):
            print(f"✓ Data Available: YES")
            print(f"  - Risk Level: {bulletin.get('risk_max')}/5")
            print(f"  - Altitude Zones: {len(bulletin.get('altitude_risks', []))}")
            print(f"  - Text Descriptions: {'YES' if bulletin.get('summary') else 'NO'}")
        else:
            print(f"⚠ Data Available: NO (may be seasonal or unavailable)")

        print()
        print("Next Steps:")
        print("  1. Review the XML structure in bra_bulletin_CHABLAIS.xml")
        print("  2. Confirm all expected fields are present")
        print("  3. Proceed with sensor implementation")
        print("=" * 80)

    except BraApiError as err:
        print(f"✗ Bulletin retrieval failed: {err}")
        return
    except Exception as err:
        print(f"✗ Unexpected error during bulletin retrieval: {err}")
        import traceback
        traceback.print_exc()
        return


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nError: Missing required API key")
        print("Usage: python test_bra_api.py <api_key> [massif_id]")
        sys.exit(1)

    api_key = sys.argv[1]
    massif_id = sys.argv[2] if len(sys.argv) > 2 else "CHABLAIS"

    # Run async test
    asyncio.run(test_bra_api(api_key, massif_id))


if __name__ == "__main__":
    main()
