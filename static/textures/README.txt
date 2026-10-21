Print textures for udchen.tw

Original procedural SVG assets, created for this site. No reference artwork
or team marks are embedded in the textures.

field-paper.svg / field-paper-dark.svg: 768px repeating tiles, combining
low-frequency pulp variation, fine fractal grain, irregular flecks, and
short curved fibers. Dark mode uses lighter fibers at lower opacity.

ink-density.svg: transparent low-frequency variation over the heading ink.
ink-wear.svg: a luminance mask with white paper coverage and irregular dark
pinholes/short scratches, creating actual gaps in the ink. The mask scales
up only for the large English name; smaller headings retain finer wear.

Text stays selectable HTML; no text is rasterized. All effects are static,
self-hosted, and limited to backgrounds and display headings. Body copy,
icons, and interactive controls do not receive masks. Enhanced contrast,
forced colors, and print use solid text without paper backgrounds.

Photographic halftones (not original procedural textures):
stadium-g2-halftone.png: Uni-Lions-provided photograph, SETN / Mirror Media,
https://www.mirrormedia.mg/external/setn_1920526 (2026-10-10).
Full frame retained. Grayscale, CLAHE 15x15%+128+2, resize to 1600px wide,
then h4x4a clustered-dot dithering; white becomes transparent. Local contrast
preserves the stands, roof beams, and infield instead of flattening the field
with a single global threshold. Compared ten treatments before selection.
flag-halftone.png: user-supplied photograph of the 外野那群人 flag; isolated
flag and pole. Red-channel separation distinguishes black lettering from the
orange cloth; sigmoidal contrast 12x42%, h4x4a clustered dots, then the existing
flag/pole silhouette mask and 380x385+48+62 crop. Compared six treatments.
No redrawn letters or invented stadium lines.
See /design-credits/ for attribution. These photographs are excluded from the
site's Creative Commons license.

sawamura-halftone.png: Sawamura Eijun illustration, Yuji Terajima / Kodansha.
Source: https://img1.gtimg.com/comic/pics/hv1/165/120/1948/126699465.jpg
Exhibition report: https://bbs.kdays.net/read/60013 (2015-10-21).
Original 640x814 frame retained, including its existing left glove-edge crop.
No generative redraw, upscaling, or invented missing details. Grayscale,
level 5%,97%, sigmoidal contrast 4x48%, then a luminance fade before h4x4a
clustered-dot screening. The fade thins the dots across the lower 44% and
outer left/right 7%/4%; it reaches paper at 90% of the image height.
Threshold 50% after screening makes white fully transparent. CSS supplies
Seido-inspired blue #234f87 and its dark-theme tint #87a9db. The illustration
is excluded from the site's Creative Commons license.
