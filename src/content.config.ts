import { defineCollection } from 'astro:content';
import { z } from 'zod';
import { glob } from 'astro/loaders';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    publishedAt: z.date(),
    updatedAt: z.date().optional(),
    author: z.string().default('Your Name'),
    authorRole: z.string().default('Founder & Webflow Developer'),
    authorBio: z.string().default(''),
    authorLinkedIn: z.string().optional(),
    category: z.string(),
    tags: z.array(z.string()).default([]),
    featuredImage: z.string().optional(),
    featuredImageAlt: z.string().optional(),
    readingTime: z.number(),
    metaTitle: z.string().optional(),
    metaDescription: z.string().optional(),
    keyTakeaways: z.array(z.string()).optional(),
    faq: z.array(z.object({ question: z.string(), answer: z.string() })).optional(),
  }),
});

export const collections = { blog };
