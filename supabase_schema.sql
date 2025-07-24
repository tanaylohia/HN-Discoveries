-- Supabase Schema for HN Discoveries

-- Posts table
CREATE TABLE IF NOT EXISTS posts (
    id BIGINT PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT,
    author VARCHAR(255),
    score INTEGER DEFAULT 0,
    num_comments INTEGER DEFAULT 0,
    created_time BIGINT NOT NULL,
    processed_at TIMESTAMP DEFAULT NOW(),
    is_startup BOOLEAN DEFAULT FALSE,
    is_innovation BOOLEAN DEFAULT FALSE,
    item_type VARCHAR(50) DEFAULT 'other'
);

-- Discoveries table (enhanced startups table)
CREATE TABLE IF NOT EXISTS discoveries (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    post_id BIGINT NOT NULL REFERENCES posts(id),
    innovation_score DECIMAL(3,1) DEFAULT 0.0,
    category TEXT,
    summary TEXT,
    why_interesting TEXT,
    key_features JSONB DEFAULT '[]'::jsonb,
    analysis JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indices for performance
CREATE INDEX IF NOT EXISTS idx_posts_created_time ON posts(created_time DESC);
CREATE INDEX IF NOT EXISTS idx_posts_item_type ON posts(item_type);
CREATE INDEX IF NOT EXISTS idx_discoveries_innovation_score ON discoveries(innovation_score DESC);
CREATE INDEX IF NOT EXISTS idx_discoveries_post_id ON discoveries(post_id);

-- View for easy querying
CREATE OR REPLACE VIEW discovery_details AS
SELECT 
    p.*,
    d.innovation_score,
    d.category,
    d.summary,
    d.why_interesting,
    d.key_features,
    d.analysis
FROM posts p
INNER JOIN discoveries d ON p.id = d.post_id
WHERE p.item_type IN ('startup', 'innovation')
ORDER BY p.created_time DESC;

-- Grant permissions (Supabase handles this automatically for anon/authenticated roles)
-- But you may need to enable RLS (Row Level Security) and create policies

-- Enable RLS
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE discoveries ENABLE ROW LEVEL SECURITY;

-- Create policies for read access (adjust as needed)
CREATE POLICY "Enable read access for all users" ON posts
    FOR SELECT USING (true);

CREATE POLICY "Enable read access for all users" ON discoveries
    FOR SELECT USING (true);

-- For write access, you'll use the service key which bypasses RLS