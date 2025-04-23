import argparse
import sys
from pathlib import Path
from typing import List, Optional
from imagecompare.core.comparators import (
    PixelComparator,
    HistogramComparator,
    PHashComparator,
    SSIMComparator
)

def main():
    parser = argparse.ArgumentParser(
        description="Image Comparison CLI Tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Main arguments
    parser.add_argument("image1", type=str, help="Path to first image")
    parser.add_argument("image2", type=str, help="Path to second image")
    
    # Comparison options
    parser.add_argument(
        "-m", "--method",
        choices=["pixel", "histogram", "phash", "ssim", "all"],
        default="phash",
        help="Comparison method to use"
    )
    parser.add_argument(
        "-t", "--threshold",
        type=float,
        default=0.85,
        help="Similarity threshold (0.0-1.0)"
    )
    parser.add_argument(
        "-o", "--output",
        choices=["simple", "json", "verbose"],
        default="simple",
        help="Output format"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize comparators
        comparators = {
            "pixel": PixelComparator(threshold=args.threshold),
            "histogram": HistogramComparator(threshold=args.threshold),
            "phash": PHashComparator(threshold=args.threshold),
            "ssim": SSIMComparator(threshold=args.threshold)
        }
        
        results = []
        
        if args.method == "all":
            methods = comparators.keys()
        else:
            methods = [args.method]
        
        for method in methods:
            comparator = comparators[method]
            is_match, confidence = comparator.compare(args.image1, args.image2)
            
            results.append({
                "method": method,
                "match": is_match,
                "confidence": confidence,
                "threshold": args.threshold
            })
        
        # Output results
        if args.output == "json":
            import json
            print(json.dumps(results, indent=2))
        elif args.output == "verbose":
            for result in results:
                print(f"Method: {result['method'].upper()}")
                print(f"  Similarity: {result['confidence']:.2f}")
                print(f"  Threshold: {result['threshold']}")
                print(f"  Match: {'YES' if result['match'] else 'NO'}\n")
        else:
            for result in results:
                print(f"{result['method']}: {'MATCH' if result['match'] else 'NO MATCH'} ({result['confidence']:.2f})")
        
        sys.exit(0 if results[0]['match'] else 1)
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()