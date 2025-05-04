import { useState, useEffect } from 'react';
import { UploadCloud, ImagePlus, CheckCircle, XCircle, AlertCircle, X } from 'lucide-react';
import './detect-duplicate.css'; // Make sure this path matches your CSS file location



//useState and useEfect hooks real world appplications 
function ImageUpload() {
  const [originalImage, setOriginalImage] = useState(null);
  const [originalPreview, setOriginalPreview] = useState(null);
  const [comparisonImages, setComparisonImages] = useState([]);
  const [imageId, setImageId] = useState(null);
  const [results, setResults] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const [trainingStatus, setTrainingStatus] = useState(null);
  const [testingStatus, setTestingStatus] = useState(null);
  const [allImages, setAllImages] = useState([]);

  // Debug useEffect to log state changes
  useEffect(() => {
    console.log('Original Preview:', originalPreview);
    console.log('Show Preview:', showPreview);
  }, [originalPreview, showPreview]);

  const handleOriginalUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    console.log('File selected:', file);

    // Check file size (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
      setError('File size should be less than 5MB');
      return;
    }

    setError(null);
    setOriginalImage(file);
    
    // Create preview URL
    const reader = new FileReader();
    reader.onloadend = () => {
      console.log('FileReader result:', reader.result);
      setOriginalPreview(reader.result);
    };
    reader.readAsDataURL(file);

    const formData = new FormData();
    formData.append('image', file);

    try {
      const response = await fetch('http://localhost:3000/api/upload/original', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to upload image');
      }

      const data = await response.json();
      console.log('Upload response:', data);
      setImageId(data.imageId);
    } catch (error) {
      console.error('Error uploading original image:', error);
      setError(error.message || 'Failed to upload original image');
    }
  };

  const handleComparisonUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (!files.length || !imageId) return;

    setError(null);
    setUploading(true);
    const newResults = [];

    for (const file of files) {
      // Check file size (5MB limit)
      if (file.size > 5 * 1024 * 1024) {
        setError('One or more files exceed the 5MB limit');
        continue;
      }

      const formData = new FormData();
      formData.append('image', file);

      try {
        const response = await fetch(`http://localhost:3000/api/upload/comparison/${imageId}`, {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Failed to upload comparison image');
        }

        const data = await response.json();
        
        const reader = new FileReader();
        reader.onloadend = () => {
          newResults.push({
            imageUrl: reader.result,
            hammingDistance: data.hammingDistance,
            similarityScore: data.similarityScore,
            pHashDistance: data.pHashDistance,
            isPirated: data.isPirated,
            detectionMethod: data.detectionMethod
          });
          setResults([...newResults]);
        };
        reader.readAsDataURL(file);
      } catch (error) {
        console.error('Error uploading comparison image:', error);
        setError(error.message || 'Failed to upload comparison image');
      }
    }

    setUploading(false);
  };

  // Function to train with multiple images
  const trainImages = async (files) => {
    try {
      setTrainingStatus('Processing images...');
      setError(null);
      
      if (files.length === 0) {
        throw new Error('No images selected');
      }

      // Store all images in array
      const imageArray = Array.from(files);
      setAllImages(imageArray);

      // Upload first image as original
      const formData = new FormData();
      formData.append('image', imageArray[0]);

      const response = await fetch('http://localhost:3000/api/upload/original', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to upload original image');
      }

      const data = await response.json();
      setImageId(data.imageId);
      setOriginalImage(imageArray[0]);
      
      // Create preview for original
      const reader = new FileReader();
      reader.onloadend = () => {
        setOriginalPreview(reader.result);
      };
      reader.readAsDataURL(imageArray[0]);

      // Clear previous results
      /// Clear previous results
      setResults([]);

      // Upload remaining images as comparisons (starting from index 1)
      const newResults = [];
      for (let i = 1; i < imageArray.length; i++) {
        const comparisonFormData = new FormData();
        comparisonFormData.append('image', imageArray[i]);

        const comparisonResponse = await fetch(`http://localhost:3000/api/upload/comparison/${data.imageId}`, {
          method: 'POST',
          body: comparisonFormData,
        });

        if (!comparisonResponse.ok) {
          throw new Error(`Failed to upload comparison image ${i}`);
        }

        const comparisonData = await comparisonResponse.json();
        
        const comparisonReader = new FileReader();
        comparisonReader.onloadend = () => {
          // Only add to results if it's not the original image
          if (i > 0) {
            newResults.push({
              imageUrl: comparisonReader.result,
              fileName: imageArray[i].name,
              hammingDistance: comparisonData.hammingDistance,
              similarityScore: comparisonData.similarityScore,
              pHashDistance: comparisonData.pHashDistance,
              isPirated: comparisonData.isPirated,
              detectionMethod: comparisonData.detectionMethod
            });
            setResults([...newResults]);
          }
        };
        comparisonReader.readAsDataURL(imageArray[i]);
      }

      setTrainingStatus(`Processing completed with ${imageArray.length} images`);
    } catch (error) {
      console.error('Error in processing:', error);
      setError(error.message);
      setTrainingStatus('Processing failed');
    }
  };

  // Function to test a single image
  const testImage = async (imageFile) => {
    try {
      setTestingStatus('Testing in progress...');
      setError(null);

      if (!imageFile) {
        throw new Error('No image file selected');
      }

      if (!imageId) {
        throw new Error('Please upload an original image first');
      }

      console.log('Testing image:', imageFile.name);
      console.log('Original image ID:', imageId);

      const formData = new FormData();
      formData.append('image', imageFile);

      console.log('Sending request to server...');
      const response = await fetch(`http://localhost:3000/api/upload/comparison/${imageId}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to test image');
      }

      const data = await response.json();
      console.log('Received response:', data);
      
      const reader = new FileReader();
      reader.onloadend = () => {
        setResults([{
          imageUrl: reader.result,
          hammingDistance: data.hammingDistance,
          similarityScore: data.similarityScore,
          pHashDistance: data.pHashDistance,
          isPirated: data.isPirated,
          detectionMethod: data.detectionMethod
        }]);
      };
      reader.readAsDataURL(imageFile);

      setTestingStatus('Testing completed');
    } catch (error) {
      console.error('Error in testing:', error);
      setError(error.message);
      setTestingStatus('Testing failed');
    }
  };

  const formatNumber = (num) => {
    if (num === null || num === undefined) return 'N/A';
    return typeof num === 'number' ? num.toFixed(4) : num;
  };

  const getStatusColor = (result) => {
    if (result.isPirated) {
      return 'status-pirated';
    }
    return 'status-not-pirated';
  };

  const getStatusMessage = (result) => {
    if (!result.hammingDistance && !result.similarityScore) {
      return 'Analysis Failed';
    }

    if (result.isPirated) {
      return `Pirated (${result.detectionMethod})`;
    }
    return 'Not Pirated';
  };

  return (
    <div className="container">
      <div className="upload-box">
        <h2 className="title" style={{color:'red'}}>Image Comparison Tool</h2>
        
        {error && (
          <div className="error-message">
            <AlertCircle className="icon-small" />
            <span>{error}</span>
          </div>
        )}
        
        {/* Training Section */}
        <div className="section">
          <h3>Select Multiple Images (First image will be original)</h3>
          <label className="file-label">
            <input 
              type="file" 
              accept="image/*" 
              multiple 
              onChange={(e) => {
                const files = Array.from(e.target.files);
                if (files.length > 10) {
                  setError('Maximum 10 images allowed');
                  return;
                }
                trainImages(files);
              }} 
              className="hidden-input" 
              disabled={uploading}
            />
            <ImagePlus className="icon" />
            <span className="label-text">
              {uploading ? 'Uploading...' : 'Select up to 10 images (first will be original)'}
            </span>
          </label>
          {trainingStatus && (
            <div className="status-message">
              {trainingStatus}
            </div>
          )}
        </div>

        {/* Testing Section */}
        <div className="section">
          <h3>Testing Mode (Single Image)</h3>
          <label className="file-label">
            <input 
              type="file" 
              accept="image/*" 
              onChange={(e) => testImage(e.target.files[0])} 
              className="hidden-input" 
              disabled={!imageId || uploading}
            />
            <ImagePlus className="icon" />
            <span className="label-text">
              {uploading ? 'Testing...' : 'Select image to test'}
            </span>
          </label>
          {testingStatus && (
            <div className="status-message">
              {testingStatus}
            </div>
          )}
        </div>

        {/* Original Image Upload */}
        <div className="section">
          <h3>Step 1: Upload Original Image</h3>
          <div className="original-image-container">
            <label className="file-label">
              <input 
                type="file" 
                accept="image/*" 
                onChange={handleOriginalUpload} 
                className="hidden-input" 
              />
              {originalPreview ? (
                <div className="thumbnail-container">
                  <img 
                    src={originalPreview} 
                    alt="Original Preview" 
                    className="thumbnail-image"
                    onClick={() => setShowPreview(true)}
                  />
                  <div className="thumbnail-overlay">
                    <span>Click to preview</span>
                  </div>
                </div>
              ) : (
                <>
                  <ImagePlus className="icon" />
                  <span className="label-text">Click to select original image</span>
                </>
              )}
            </label>
          </div>
        </div>

        {/* Image Preview Modal */}
        {showPreview && originalPreview && (
          <div className="preview-modal" onClick={() => setShowPreview(false)}>
            <div className="preview-content" onClick={e => e.stopPropagation()}>
              <button className="close-button" onClick={() => setShowPreview(false)}>
                <X className="icon-small" />
              </button>
              <img src={originalPreview} alt="Original Preview" className="preview-full-image" />
            </div>
          </div>
        )}

        {/* Comparison Images Upload */}
        <div className="section">
          <h3>Step 2: Upload Comparison Images</h3>
          <label className="file-label">
            <input 
              type="file" 
              accept="image/*" 
              multiple 
              onChange={handleComparisonUpload} 
              className="hidden-input" 
              disabled={!imageId || uploading}
            />
            <ImagePlus className="icon" />
            <span className="label-text">
              {uploading ? 'Uploading...' : 'Click to select comparison images'}
            </span>
          </label>
        </div>

        {/* Results Display */}
        {/* Results Display */}
        {results.length > 0 && (
          <div className="results-section">
            <h3>Comparison Results</h3>
            <div className="results-grid">
              {results.map((result, index) => (
                <div key={index} className="result-card">
                  <div className="card-header">
                    <div className="comparison-image">
                      <img src={result.imageUrl} alt={`Comparison ${index + 1}`} />
                      <div className="image-name">{result.fileName}</div>
                    </div>
                    <div className="comparison-details">
                      <div className="method-info">
                        <span className="method-label">Detection Method:  </span>
                        <span className="method-value">{result.detectionMethod}</span>
                      </div>
                      <div className="scores">
                        <div className="score-item"> 
                          <span className="score-label">Hamming Distance:  </span>
                          <span className="score-value">
                            {formatNumber(result.hammingDistance)}
                            {result.hammingDistance < 50 && <span className="threshold-indicator">(Below Threshold)</span>}
                          </span>
                        </div>
                        <div className="score-item">
                          <span className="score-label">Similarity Score:   </span>
                          <span className="score-value">
                            {formatNumber(result.similarityScore)}
                            {result.similarityScore > 0.6 && <span className="threshold-indicator">(Above Threshold)</span>}
                          </span>
                        </div>
                        <div className="score-item">
                          <span className="score-label">Perceptual Hash Distance:   </span>
                          <span className="score-value">
                            {formatNumber(result.pHashDistance)}
                            {result.pHashDistance !== null && result.pHashDistance < 15 && <span className="threshold-indicator">(Match)</span>}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className={`result-status ${result.isPirated ? 'pirated' : 'not-pirated'}`}>
                    <div className="status-icon">
                      {result.isPirated ? 
                        <XCircle className="icon-pirated" size={20} /> : 
                        <CheckCircle className="icon-original" size={20} />
                      }
                    </div>
                    <span className="status-text">
                      {result.isPirated ? 'Pirated Content' : 'Original Content'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ImageUpload;
