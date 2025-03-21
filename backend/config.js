module.exports = {
  jwtSecret: process.env.JWT_SECRET || 'porthealth_jwt_secret',
  db: {
    database: process.env.DB_NAME || 'porthealth',
    username: process.env.DB_USER || 'porthealth_user',
    password: process.env.DB_PASS || 'password123',
    host: process.env.DB_HOST || 'localhost',
    port: 5432,  // Ensure this is set to 5432
    dialect: 'postgres'
  }
};
