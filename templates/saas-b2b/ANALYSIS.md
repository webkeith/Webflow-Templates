# saas-b2b — source analysis (3rddegreescreening.com homepage)

Read on 26 Nov 2026 from the live page's content and structure. I couldn't inspect the rendered visuals (colours, type, spacing): browser access needed a permission click that timed out. So this template reproduces **section patterns only**, in a neutral Relume-style wireframe with placeholder copy and placeholder media. It carries none of 3rd Degree's copy, logos, images or brand styling.

## Page anatomy → blocks

| # | Source section | Pattern | Block |
|---|---|---|---|
| 1 | Header with 7 dropdowns (two very long: 20 services, 21 industries), Login / Pricing / Contact Us | Navbar with simple and mega dropdowns plus utility links | `navbar1` |
| 2 | Hero: headline, sub, Start Now / Schedule a Call, background video, 4 accreditation badges | Dark media hero + trust row | `header1` |
| 3 | How it works: 4 steps + demo link | Numbered vertical steps + media | `process1` |
| 4 | Adjudication intelligence: 3 features with links, stats panel over laptop mockup, demo link | Feature list + floating stats card | `feature1` |
| 5 | Identity verification lead magnet: email + button, "No spam" note | Inline signup card | `signup1` |
| 6 | Customer experience: video + copy | Media + text | `layout1` |
| 7 | "Every check you need": 3 checkmarks + state map + "View all locations" | Checklist + map | `feature2` |
| 8 | "Not your typical background check": image + 3 features + link | Centered header, image + icon list | `layout2` |
| 9 | 3 testimonials with title, quote, initial avatar, name, role | Three testimonial cards | `testimonial1` |
| 10 | Pricing: 3 packages, middle "Most Popular", per-unit price, turnaround, feature lists, footnotes | Three-plan pricing | `pricing1` |
| 11 | ATS partners: 8 logos repeated 4× (marquee) | Infinite logo marquee | `logo1` |
| 12 | Compliance: 4 features, 4 stats, dashboard image + caption | 2×2 features + stat row + wide image | `feature3` |
| 13 | Blog: 3 cards with tag, category, read time, author, date, Read link, View all | Three blog cards | `blog1` |
| 14 | Contact: 4 benefit checks + form (name, company, email, phone, 2 selects, message) | Benefits + form card | `contact1` |
| 15 | Footer: brand, description, 2 links, 4 socials, badge, 5 link columns, legal row | Brand + five columns | `footer1` |

## Observations worth carrying into the system

- **The CTAs compete.** The navbar has Login, Pricing and Contact Us; the hero has Start Now and Schedule a Call; there are two separate demo links. The template keeps one primary and one secondary action per block.
- **Mega menus with 20+ items** need columns and a mobile accordion. `navbar1` handles both.
- **The marquee duplicates its logo list in the DOM four times.** `logo1` uses two tracks, with the second marked `aria-hidden`, so screen readers hear the list once. The animation pauses on hover and stops under reduced motion.
- **Forms carry a security check** (likely Turnstile or reCAPTCHA) that disables the submit button. Webflow's native Form Block plus its spam protection is the equivalent; see the README.

## Small Business solution page (/solution/background-checks-for-small-business)

Read on 27 Nov 2026. Sections already covered by existing blocks were not duplicated:
- the testimonials match `testimonial1`
- the contact form matches `contact1`
- the footer matches `footer1`

| Source section | Pattern | Block | Image key |
|---|---|---|---|
| Hero: tagline, H1, two buttons, image anchored to the section bottom, floating "check complete" card, four accreditation badges | Split hero, status card, trust band | `header2` | `feature-laptop` |
| "Why choose": five benefits around a central illustration | Benefits around a central image | `feature4` | `workspace-flatlay` |
| Four stats with value, label and detail | Big-number band | `stats1` | — |
| "How it works": four horizontal steps | Horizontal numbered steps (scroll reveal) | `process2` | — |
| "What you get": three alternating rows with highlighted takeaways | Alternating image rows | `layout3` | `architecture`, `portrait-support`, `meeting-conversation` |
| Newsletter: image, heading, email signup | Newsletter with image | `signup2` | `landscape-dusk` |

All copy is placeholder text. The source's accreditation logos and the US flag are replaced with neutral icons.
