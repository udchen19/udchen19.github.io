---
# Leave the homepage title empty to use the site title
title: ''
date: 2022-10-24
type: landing

design:
  # Default section spacing
  spacing: '1rem'

sections:
  # Biography block - Uses the new, more comprehensive resume-biography-3 block.
  # It pulls data from your `content/authors/admin/_index.md` file.
  - block: resume-biography
    id: about # Added ID to match your navigation menu
    content:
      username: admin
      text: ''
      headings:
        about: ''
        education: ''
        interests: ''
    design:
      css_class: hbx-bg-gradient
      avatar:
        size: medium
        shape: circle
      columns: "1"

  # Projects block - Restored from your old homepage.
  - block: collection
    id: projects
    content:
      title: Projects
      filters:
        folders:
          - project
    design:
      view: article-grid
      fill_image: false
      columns: "2"
      show_date: false
      show_read_time: false
      show_read_more: false

  # Featured Publications block - A useful addition from the new theme for an academic site.
  # To feature a publication, set `featured: true` in its front matter.
  - block: collection
    id: publications
    content:
      title: Featured Publications
      filters:
        folders:
          - publication
        featured_only: true

    design:
      view: citation
      show_read_more: true

  # Skills block - Restored from your old homepage.
  # - block: resume-skills
  #   content:
  #     title: Skills
  #     text: ''
  #     username: admin
  #   design:
  #     columns: '3'

  # - block: resume-experience
  #   content:
  #     username: admin
  #   design:
  #     # Hugo date format
  #     date_format: 'January 2006'
  #     # Education or Experience section first?
  #     is_education_first: false

  # - block: resume-languages
  #   content:
  #     title: Languages
  #     text: ''
  #     username: admin
  #   design:
  #     columns: '1'

  # Recent Posts block - Adapted from your old homepage settings.
  - block: collection
    id: posts
    content:
      title: Recent Posts
      count: 6
      filters:
        folders:
          - post
      order: desc
    design:
      view: article-grid
      columns: '2'

---