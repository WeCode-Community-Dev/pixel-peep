const mongoose = require('mongoose');

async function testConnection() {
  try {
    console.log('Attempting to connect to MongoDB...');
    await mongoose.connect('mongodb://127.0.0.1:27017/image-comparison?directConnection=true&serverSelectionTimeoutMS=2000', {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    console.log('Successfully connected to MongoDB!');
    
    // Test creating a collection
    const Test = mongoose.model('Test', new mongoose.Schema({ name: String }));
    await Test.create({ name: 'test' });
    console.log('Successfully created test document!');
    
    // Clean up
    await Test.deleteMany({});
    console.log('Cleaned up test documents');
    
    process.exit(0);
  } catch (error) {
    console.error('Error:', error);
    process.exit(1);
  }
}

testConnection(); 