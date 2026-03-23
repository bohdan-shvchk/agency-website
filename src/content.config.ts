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

const projects = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/projects' }),
  schema: z.object({
    title: z.string(),
    tagline: z.string(),
    description: z.string(),
    industry: z.string(),
    services: z.array(z.string()),
    year: z.string(),
    url: z.string().optional(),
    color: z.string().default('#000000'),
    // Metrics shown as highlight numbers
    metrics: z.array(z.object({
      value: z.string(),
      label: z.string(),
    })).optional(),
    // Challenge → What we did → Result
    challenge: z.string(),
    solution: z.string(),
    result: z.string(),
    // Detailed process steps
    process: z.array(z.object({
      step: z.string(),
      title: z.string(),
      body: z.string(),
    })).optional(),
    // Tech/tools used
    stack: z.array(z.string()).default([]),
    // Testimonial
    testimonial: z.object({
      quote: z.string(),
      author: z.string(),
      role: z.string(),
    }).optional(),
    metaTitle: z.string().optional(),
    metaDescription: z.string().optional(),
    order: z.number().default(99),
  }),
});

export const collections = { blog, projects };
