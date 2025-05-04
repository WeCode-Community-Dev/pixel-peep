const express = require('express');
const mongoose = require('mongoose');
const multer = require('multer');
const sharp = require('sharp');
const cors = require('cors');
const path = require('path');
const crypto = require('crypto');
require('dotenv').config();


const app = express();
app.use(cors());
app.use(express.json());

// MongoDB connection with better error handling
const mongoURI = 'mongodb://127.0.0.1:27017/image-comparison?directConnection=true&serverSelectionTimeoutMS=2000';

console.log('Attempting to connect to MongoDB with URI:', mongoURI);

mongoose.connect(mongoURI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,

})
.then(() => {
  console.log('Connected to MongoDB successfully');
})
.catch((err) => {
  console.error('MongoDB connection error:', err);
  console.log('Connection URI used:', mongoURI);
});

// Image schema
const imageSchema = new mongoose.Schema({
  originalImage: { type: String, required: true },
  comparisonImages: [{
    imageUrl: String,
    hammingDistance: Number,
    similarityScore: Number,
    isPirated: Boolean,
    detectionMethod: String
  }],
  createdAt: { type: Date, default: Date.now }
});

const Image = mongoose.model('Image', imageSchema);

// Configure multer for file upload
const storage = multer.memoryStorage();
const upload = multer({ 
  storage: storage,
  limits: {
    fileSize: 5 * 1024 * 1024 // 5MB limit
  }
});

// Function to calculate Hamming distance between two images
async function calculateHammingDistance(originalBuffer, comparisonBuffer) {
  try {
    // Resize both images to a larger size for better comparison
    const originalResized = await sharp(originalBuffer)
      .resize(64, 64)  // Increased size for better detail
      .modulate({ brightness: 1, saturation: 1 }) // Normalize brightness and saturation
      .grayscale()
      .blur(0.5) // Slight blur to reduce noise
      .raw()
      .toBuffer();

    const comparisonResized = await sharp(comparisonBuffer)
      .resize(64, 64)
      .modulate({ brightness: 1, saturation: 1 })
      .grayscale()
      .blur(0.5)
      .raw()
      .toBuffer();

    let distance = 0;
    for (let i = 0; i < originalResized.length; i++) {
      distance += Math.abs(originalResized[i] - comparisonResized[i]);
    }

    // Normalize the distance value
    return distance / originalResized.length;
  } catch (error) {
    console.error('Error in calculateHammingDistance:', error);
    throw new Error('Failed to process image for comparison');
  }
}

// Function to calculate image similarity
async function calculateImageSimilarity(originalBuffer, comparisonBuffer) {
  try {
    // Process images with more robust preprocessing
    const originalResized = await sharp(originalBuffer)
      .resize(256, 256)
      .modulate({ brightness: 1, saturation: 1 })
      .normalize() // Normalize pixel values
      .blur(0.5)
      .grayscale()
      .raw()
      .toBuffer();

    const comparisonResized = await sharp(comparisonBuffer)
      .resize(256, 256)
      .modulate({ brightness: 1, saturation: 1 })
      .normalize()
      .blur(0.5)
      .grayscale()
      .raw()
      .toBuffer();

    // Calculate mean and standard deviation
    let originalSum = 0;
    let comparisonSum = 0;
    let originalSumSq = 0;
    let comparisonSumSq = 0;
    let crossSum = 0;
    const totalPixels = originalResized.length;

    for (let i = 0; i < totalPixels; i++) {
      originalSum += originalResized[i];
      comparisonSum += comparisonResized[i];
      originalSumSq += originalResized[i] * originalResized[i];
      comparisonSumSq += comparisonResized[i] * comparisonResized[i];
      crossSum += originalResized[i] * comparisonResized[i];
    }

    const originalMean = originalSum / totalPixels;
    const comparisonMean = comparisonSum / totalPixels;
    const originalVar = (originalSumSq / totalPixels) - (originalMean * originalMean);
    const comparisonVar = (comparisonSumSq / totalPixels) - (comparisonMean * comparisonMean);
    const covariance = (crossSum / totalPixels) - (originalMean * comparisonMean);

    // Calculate normalized cross-correlation
    const ncc = covariance / Math.sqrt(originalVar * comparisonVar);
    
    // Convert to similarity score (0 to 1)
    return (ncc + 1) / 2;
  } catch (error) {
    console.error('Error in calculateImageSimilarity:', error);
    throw new Error('Failed to calculate image similarity');
  }
}

// Add pHash calculation function
async function calculatePHash(imageBuffer) {
  try {
    // Resize image to 32x32 and convert to grayscale
    const resized = await sharp(imageBuffer)
      .resize(32, 32)
      .grayscale()
      .raw()
      .toBuffer();

    // Calculate DCT (Discrete Cosine Transform)
    const dct = new Array(32 * 32).fill(0);
    for (let u = 0; u < 32; u++) {
      for (let v = 0; v < 32; v++) {
        let sum = 0;
        for (let x = 0; x < 32; x++) {
          for (let y = 0; y < 32; y++) {
            sum += resized[x * 32 + y] * 
              Math.cos((2 * x + 1) * u * Math.PI / 64) * 
              Math.cos((2 * y + 1) * v * Math.PI / 64);
          }
        }
        dct[u * 32 + v] = sum;
      }
    }

    // Take the top-left 8x8 of the DCT
    const hash = [];
    for (let i = 0; i < 8; i++) {
      for (let j = 0; j < 8; j++) {
        hash.push(dct[i * 32 + j]);
      }
    }

    // Calculate mean of the 8x8 DCT
    const mean = hash.reduce((a, b) => a + b, 0) / 64;

    // Generate binary hash
    return hash.map(val => val > mean ? '1' : '0').join('');
  } catch (error) {
    console.error('Error calculating pHash:', error);
    return null;
  }
}

// Add function to calculate Hamming distance between two hashes
function calculateHammingDistance(hash1, hash2) {
  if (!hash1 || !hash2 || hash1.length !== hash2.length) return null;
  let distance = 0;
  for (let i = 0; i < hash1.length; i++) {
    if (hash1[i] !== hash2[i]) distance++;
  }
  return distance;
}

// Upload original image
app.post('/api/upload/original', upload.single('image'), async (req, res) => {
  try {
    console.log('Received original image upload request');
    
    if (!req.file) {
      return res.status(400).json({ error: 'No image file provided' });
    }

    console.log('Processing image...');
    const image = new Image({
      originalImage: req.file.buffer.toString('base64')
    });

    console.log('Saving to database...');
    await image.save();
    console.log('Image saved successfully');

    res.json({ 
      success: true, 
      imageId: image._id,
      message: 'Original image uploaded successfully'
    });
  } catch (error) {
    console.error('Error in original image upload:', error);
    res.status(500).json({ 
      error: 'Failed to upload original image',
      details: error.message 
    });
  }
});

// Upload comparison image
app.post('/api/upload/comparison/:imageId', upload.single('image'), async (req, res) => {
  try {
    console.log('Received comparison image upload request');
    
    if (!req.file) {
      return res.status(400).json({ error: 'No image file provided' });
    }

    const image = await Image.findById(req.params.imageId);
    if (!image) {
      return res.status(404).json({ error: 'Original image not found' });
    }

    const originalBuffer = Buffer.from(image.originalImage, 'base64');
    const comparisonBuffer = req.file.buffer;
    
    // Calculate pHash for both images
    const originalPHash = await calculatePHash(originalBuffer);
    const comparisonPHash = await calculatePHash(comparisonBuffer);
    
    // Calculate pHash distance
    const pHashDistance = calculateHammingDistance(originalPHash, comparisonPHash);
    
    // Calculate existing metrics
    const hammingDistance = await calculateHammingDistance(originalBuffer, comparisonBuffer);
    const similarityScore = await calculateImageSimilarity(originalBuffer, comparisonBuffer);
    
    // Determine if pirated based on all metrics
    const isPirated = hammingDistance < 50 || 
                     similarityScore > 0.6 || 
                     (pHashDistance !== null && pHashDistance < 15);
    
    let detectionMethod = 'Combined Analysis';
    if (hammingDistance < 50) detectionMethod = 'Hamming Distance';
    else if (similarityScore > 0.6) detectionMethod = 'Similarity Score';
    else if (pHashDistance !== null && pHashDistance < 15) detectionMethod = 'Perceptual Hash';

    // Store the results
    image.comparisonImages.push({
      imageUrl: req.file.buffer.toString('base64'),
      hammingDistance,
      similarityScore,
      pHashDistance,
      isPirated,
      detectionMethod
    });

    await image.save();
    console.log('Comparison image processed successfully');

    res.json({
      hammingDistance,
      similarityScore,
      pHashDistance,
      isPirated,
      detectionMethod
    });
  } catch (error) {
    console.error('Error processing comparison:', error);
    res.status(500).json({ error: 'Error processing comparison' });
  }
});

// Get comparison results
app.get('/api/results/:imageId', async (req, res) => {
  try {
    const image = await Image.findById(req.params.imageId);
    if (!image) {
      return res.status(404).json({ error: 'Image not found' });
    }
    res.json(image);
  } catch (error) {
    console.error('Error fetching results:', error);
    res.status(500).json({ 
      error: 'Failed to fetch results',
      details: error.message 
    });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
}); 