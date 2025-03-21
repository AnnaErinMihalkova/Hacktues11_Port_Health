const { Pool } = require('pg');
const pool = new Pool({
  host: process.env.PGHOST || 'localhost',
  user: process.env.PGUSER || 'postgres',
  password: process.env.PGPASSWORD || 'bazadanni',
  database: process.env.PGDATABASE || 'porthealth',
  port: process.env.PGPORT || 5432
});
module.exports = pool;
