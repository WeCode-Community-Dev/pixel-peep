const express = require('express')
const multer = require('multer');
const path = require('path');
const sharp = require("sharp");
const { imageHash } = require("image-hash");
const app = express()
const port = 3000

app.use(express.static('public'))

// Setup multer storage
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/');
  },
  filename: (req, file, cb) => {
    cb(null, file.originalname);
  }
});

// Filter to accept only images
const fileFilter = (req, file, cb) => {
  const allowedTypes = /jpeg|jpg|png/;
  const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
  const mimetype = allowedTypes.test(file.mimetype);

  if (extname && mimetype) {
    return cb(null, true);
  } else {
    cb(new Error('Only image files are allowed!'));
  }
};

// Multer config
const upload = multer({
  storage: storage,
  fileFilter: fileFilter
});

app.post('/upload', upload.fields([
  { name: 'image1', maxCount: 1 },
  { name: 'image2', maxCount: 1 }
]), (req, res) => {
  if (!req.files || !req.files['image1'] || !req.files['image2']) {
    return res.status(400).send('Both images are required!');
  }

  // pHash
  async function pHash(img) {
    const processedImage = await sharp(img)
      .resize(256, 256)
      .grayscale()
      .toFormat("jpeg")
      .toBuffer();

    return new Promise((resolve, reject) => {
      imageHash({ data: processedImage }, 16, true, (err, hash) => {
        resolve(hash);
        if (err) reject(err);
      });
    });
  }

  // dHash
  async function dHash(img) {
    const { data } = await sharp(img)
      .resize(9, 8)
      .grayscale()
      .raw()
      .toBuffer({ resolveWithObject: true });

    let bits = '';
    for (let y = 0; y < 8; y++) {
      for (let x = 0; x < 8; x++) {
        const left = data[y * 9 + x];
        const right = data[y * 9 + x + 1];
        bits += left < right ? '1' : '0';
      }
    }

    const hexHash = BigInt('0b' + bits).toString(16).padStart(16, '0');
    return hexHash;
  }

  // Compareing using Hamming distance
  function hexToBin(hex) {
    return hex.split('').map(h => parseInt(h, 16).toString(2).padStart(4, '0')).join('');
  }

  function hammingDist(hash1, hash2) {
    const bin1 = hexToBin(hash1);
    const bin2 = hexToBin(hash2);
    return [...bin1].reduce((acc, val, idx) => acc + (val !== bin2[idx] ? 1 : 0), 0);
  }

  async function compareImg(img1, img2, threshold = { p: 10, d: 10 }) {
    const [pHash1, pHash2] = await Promise.all([
      pHash(img1),
      pHash(img2),
    ]);

    const [dHash1, dHash2] = await Promise.all([
      dHash(img1),
      dHash(img2),  
    ]);

    const pDist = hammingDist(pHash1, pHash2);
    const dDist = hammingDist(dHash1, dHash2);

    const isSimilar = pDist <= threshold.p || dDist <= threshold.d;

    return {
      isSimilar
    };       
  }

  (async () => {
    const image1 = req.files['image1'][0].path;
    const image2 = req.files['image2'][0].path;

    const res = await compareImg(image1, image2)

    let finalRes = res.isSimilar ? "The images are similar!" : " The images are different";
    console.log(finalRes);
  })();

  res.send("Thanks for uploading!");
  
});


app.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
})