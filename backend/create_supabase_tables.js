/**
 * Create Supabase Tables Script
 * 
 * This script directly creates the necessary tables in Supabase using the 
 * Supabase JavaScript client, which handles the connection more reliably.
 */

require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');

// Get environment variables
const supabaseUrl = process.env.SUPABASE_PROJECT_URL;
const supabaseKey = process.env.SUPABASE_API_KEY;

// Create Supabase client
const supabase = createClient(supabaseUrl, supabaseKey);

// Log configuration info
console.log('====== Supabase Table Creation Tool ======');
console.log(`Using Supabase URL: ${supabaseUrl}`);

async function createTables() {
  try {
    // Create health check table
    console.log('Creating health_check table...');
    const { data: healthCheck, error: healthCheckError } = await supabase.rpc('execute_sql', {
      sql_statement: `
        CREATE TABLE IF NOT EXISTS health_check (
          id SERIAL PRIMARY KEY,
          status VARCHAR(50) DEFAULT 'OK',
          checked_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
      `
    });
    if (healthCheckError) {
      console.error('❌ Error creating health_check table:', healthCheckError.message);
    } else {
      console.log('✅ Health check table created');
      
      // Insert initial health check record
      const { error: insertError } = await supabase.rpc('execute_sql', {
        sql_statement: `INSERT INTO health_check (status) VALUES ('OK');`
      });
      if (insertError) {
        console.error('❌ Error inserting health check record:', insertError.message);
      } else {
        console.log('✅ Health check record inserted');
      }
    }

    // Create organizations table
    console.log('Creating organizations table...');
    const { error: orgError } = await supabase.rpc('execute_sql', {
      sql_statement: `
        CREATE TABLE IF NOT EXISTS organizations (
          id SERIAL PRIMARY KEY,
          name VARCHAR(255) NOT NULL,
          description TEXT,
          website VARCHAR(255),
          logo_url VARCHAR(255),
          headquarters_country VARCHAR(100),
          headquarters_city VARCHAR(100),
          founded_year INTEGER,
          contact_email VARCHAR(255),
          contact_phone VARCHAR(50),
          social_media_links JSONB,
          ai_domains JSONB,
          geographic_scopes JSONB,
          
          -- Organization role fields
          role VARCHAR(20) CHECK (role IN ('provider', 'recipient', 'both')),
          provider_type VARCHAR(50) CHECK (provider_type IN ('granting_agency', 'venture_capital', 'angel_investor', 'accelerator', NULL)),
          recipient_type VARCHAR(50) CHECK (recipient_type IN ('grantee', 'startup', 'research_institution', 'non_profit', NULL)),
          startup_stage VARCHAR(50) CHECK (startup_stage IN ('idea', 'prototype', 'seed', 'early_growth', 'expansion', NULL)),
          
          -- Equity and inclusion tracking
          women_led BOOLEAN DEFAULT FALSE,
          underrepresented_led BOOLEAN DEFAULT FALSE,
          inclusion_details JSONB,
          equity_score FLOAT,
          
          created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
      `
    });
    if (orgError) {
      console.error('❌ Error creating organizations table:', orgError.message);
    } else {
      console.log('✅ Organizations table created');
      
      // Create indexes for organizations table
      const orgIndexes = [
        `CREATE INDEX IF NOT EXISTS idx_organizations_role ON organizations(role);`,
        `CREATE INDEX IF NOT EXISTS idx_organizations_provider_type ON organizations(provider_type);`,
        `CREATE INDEX IF NOT EXISTS idx_organizations_recipient_type ON organizations(recipient_type);`,
        `CREATE INDEX IF NOT EXISTS idx_organizations_women_led ON organizations(women_led);`,
        `CREATE INDEX IF NOT EXISTS idx_organizations_underrepresented_led ON organizations(underrepresented_led);`
      ];
      
      for (const idx of orgIndexes) {
        const { error: idxError } = await supabase.rpc('execute_sql', { sql_statement: idx });
        if (idxError) {
          console.error(`❌ Error creating index: ${idx}`, idxError.message);
        }
      }
      
      console.log('✅ Organization indexes created');
    }

    // Create funding_types table
    console.log('Creating funding_types table...');
    const { error: typeError } = await supabase.rpc('execute_sql', {
      sql_statement: `
        CREATE TABLE IF NOT EXISTS funding_types (
          id SERIAL PRIMARY KEY,
          name VARCHAR(100) NOT NULL,
          description TEXT,
          
          -- Enhanced funding category tracking
          category VARCHAR(50) CHECK (category IN ('grant', 'investment', 'prize', 'other')),
          requires_equity BOOLEAN DEFAULT FALSE,
          requires_repayment BOOLEAN DEFAULT FALSE,
          typical_duration_months INTEGER,
          
          created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
      `
    });
    if (typeError) {
      console.error('❌ Error creating funding_types table:', typeError.message);
    } else {
      console.log('✅ Funding types table created');
      
      // Create indexes for funding_types table
      const { error: typeIdxError } = await supabase.rpc('execute_sql', {
        sql_statement: `CREATE INDEX IF NOT EXISTS idx_funding_types_category ON funding_types(category);`
      });
      if (typeIdxError) {
        console.error('❌ Error creating funding type index:', typeIdxError.message);
      } else {
        console.log('✅ Funding type index created');
      }
    }

    // Create funding_opportunities table
    console.log('Creating funding_opportunities table...');
    const { error: oppsError } = await supabase.rpc('execute_sql', {
      sql_statement: `
        CREATE TABLE IF NOT EXISTS funding_opportunities (
          id SERIAL PRIMARY KEY,
          title VARCHAR(255) NOT NULL,
          description TEXT NOT NULL,
          amount_min NUMERIC,
          amount_max NUMERIC,
          application_deadline DATE,
          application_url VARCHAR(255),
          eligibility_criteria JSONB,
          ai_domains JSONB,
          geographic_scopes JSONB,
          funding_type_id INTEGER REFERENCES funding_types(id),
          
          -- Organization relationship fields with enhanced roles
          provider_organization_id INTEGER REFERENCES organizations(id),
          recipient_organization_id INTEGER REFERENCES organizations(id),
          
          -- Grant-specific properties
          grant_reporting_requirements TEXT,
          grant_duration_months INTEGER,
          grant_renewable BOOLEAN DEFAULT FALSE,
          
          -- Investment-specific properties
          equity_percentage FLOAT,
          valuation_cap NUMERIC,
          interest_rate FLOAT,
          expected_roi FLOAT,
          
          -- Additional fields
          status VARCHAR(50) DEFAULT 'active',
          additional_resources JSONB,
          equity_focus_details JSONB,
          women_focus BOOLEAN DEFAULT FALSE,
          underserved_focus BOOLEAN DEFAULT FALSE,
          youth_focus BOOLEAN DEFAULT FALSE,
          
          created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
      `
    });
    if (oppsError) {
      console.error('❌ Error creating funding_opportunities table:', oppsError.message);
    } else {
      console.log('✅ Funding opportunities table created');
      
      // Create indexes for funding_opportunities table
      const oppsIndexes = [
        `CREATE INDEX IF NOT EXISTS idx_funding_opportunities_provider_org ON funding_opportunities(provider_organization_id);`,
        `CREATE INDEX IF NOT EXISTS idx_funding_opportunities_recipient_org ON funding_opportunities(recipient_organization_id);`,
        `CREATE INDEX IF NOT EXISTS idx_funding_opportunities_funding_type ON funding_opportunities(funding_type_id);`,
        `CREATE INDEX IF NOT EXISTS idx_funding_opportunities_women_focus ON funding_opportunities(women_focus);`,
        `CREATE INDEX IF NOT EXISTS idx_funding_opportunities_underserved_focus ON funding_opportunities(underserved_focus);`,
        `CREATE INDEX IF NOT EXISTS idx_funding_opportunities_youth_focus ON funding_opportunities(youth_focus);`
      ];
      
      for (const idx of oppsIndexes) {
        const { error: idxError } = await supabase.rpc('execute_sql', { sql_statement: idx });
        if (idxError) {
          console.error(`❌ Error creating index: ${idx}`, idxError.message);
        }
      }
      
      console.log('✅ Funding opportunity indexes created');
    }

    console.log('\n🎉 Success! Database tables created successfully.');
    console.log('\nYour database is now set up with:');
    console.log('- Organization role distinctions (provider/recipient)');
    console.log('- Funding type categories (grant/investment/prize/other)');
    console.log('- Grant-specific and investment-specific properties');
    console.log('- Equity and inclusion tracking fields');
    
  } catch (error) {
    console.error('❌ Unexpected error:', error.message);
  }
}

// Run the table creation process
createTables();
