"""OCR module using macOS Vision framework."""

from pathlib import Path

import Quartz
from Foundation import NSURL
from Vision import (
    VNImageRequestHandler,
    VNRecognizeTextRequest,
)


def perform_ocr(image_path: Path, languages: list[str] | None = None) -> list[dict]:
    """Perform OCR on an image using macOS Vision framework.
    
    Args:
        image_path: Path to the image file
        languages: List of language codes (e.g., ['ja', 'en']). If None, uses automatic detection.
        
    Returns:
        List of recognized text blocks with their bounding boxes and confidence
    """
    if languages is None:
        languages = ["ja-JP", "en-US"]
    
    # Load the image
    image_url = NSURL.fileURLWithPath_(str(image_path))
    
    # Create CGImage from file
    image_source = Quartz.CGImageSourceCreateWithURL(image_url, None)
    if image_source is None:
        raise ValueError(f"Could not load image from {image_path}")
    
    cg_image = Quartz.CGImageSourceCreateImageAtIndex(image_source, 0, None)
    if cg_image is None:
        raise ValueError(f"Could not create image from {image_path}")
    
    # Create request handler
    handler = VNImageRequestHandler.alloc().initWithCGImage_options_(cg_image, None)
    
    # Create text recognition request
    request = VNRecognizeTextRequest.alloc().init()
    request.setRecognitionLevel_(1)  # VNRequestTextRecognitionLevelAccurate
    request.setRecognitionLanguages_(languages)
    request.setUsesLanguageCorrection_(True)
    
    # Perform the request
    success, error = handler.performRequests_error_([request], None)
    
    if not success:
        raise RuntimeError(f"OCR failed: {error}")
    
    # Extract results
    results = []
    observations = request.results()
    
    if observations:
        for observation in observations:
            # Get the top candidate
            candidates = observation.topCandidates_(1)
            if candidates and len(candidates) > 0:
                candidate = candidates[0]
                text = candidate.string()
                confidence = candidate.confidence()
                
                # Get bounding box (normalized coordinates)
                bbox = observation.boundingBox()
                
                results.append({
                    "text": text,
                    "confidence": confidence,
                    "bbox": {
                        "x": bbox.origin.x,
                        "y": bbox.origin.y,
                        "width": bbox.size.width,
                        "height": bbox.size.height,
                    },
                })
    
    return results


def extract_text_lines(image_path: Path, languages: list[str] | None = None) -> list[str]:
    """Extract text lines from an image, sorted by vertical position.
    
    Args:
        image_path: Path to the image file
        languages: List of language codes
        
    Returns:
        List of text strings, sorted from top to bottom
    """
    results = perform_ocr(image_path, languages)
    
    # Sort by y position (note: Vision uses bottom-left origin, so we invert)
    results.sort(key=lambda r: -r["bbox"]["y"])
    
    return [r["text"] for r in results]


def extract_all_text(image_path: Path, languages: list[str] | None = None) -> str:
    """Extract all text from an image as a single string.
    
    Args:
        image_path: Path to the image file
        languages: List of language codes
        
    Returns:
        All text concatenated with newlines
    """
    lines = extract_text_lines(image_path, languages)
    return "\n".join(lines)
