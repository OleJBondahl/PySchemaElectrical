
#let a3_drawing(
  drawing_number: "DWG-000",
  revision: "00",
  author: "Author",
  drawing_name: "Drawing Name",
  project: "Project",
  frame_path: none,
  logo_path: none,
  font_family: "Times New Roman",
  body
) = {
  set page(
    paper: "a3",
    flipped: true,
    margin: 0mm,
    background: {
      if frame_path != none {
        image(frame_path, width: 100%, height: 100%)
      }
    },
    foreground: {
      let offset_x = 10mm
      let offset_y = 10mm

      place(
        bottom + right,
        dx: -offset_x,
        dy: -offset_y,

        grid(
          columns: (auto, auto),
          gutter: 5pt,

          // Title block table
          block(
            width: 130mm,
            stroke: 0.5pt,
            fill: white,
            inset: 0pt,
            grid(
              columns: (1.5fr, 0.7fr),
              rows: (7mm, 7mm, 5mm),
              stroke: 0.5pt,
              inset: 5pt,

              align(left + horizon, strong(text(10pt, [Drawing Name: #drawing_name]))),
              align(left + horizon, text(10pt, [Project: #project])),
              align(left + horizon, text(10pt, [Drawing Nr.: #drawing_number])),
              align(left + horizon, text(10pt, [Rev: #revision])),
              align(left + horizon, text(9pt, [Author: #author])),
              align(right + horizon, text(9pt, [Page #context counter(page).display() / #context counter(page).final().at(0)]))
            )
          ),

          // Logo (optional)
          if logo_path != none {
            box(height: 19mm, width: auto, inset: (left: 0pt))[
               #align(bottom)[
                 #move(dx: -0.5mm, dy: -0.2mm)[
                   #image(logo_path, height: 18mm)
                 ]
               ]
            ]
          } else {
            // Empty box placeholder when no logo
            box(height: 19mm, width: 0pt)
          }
        )
      )
    },
    footer: none
  )

  set text(size: 11pt, font: font_family)

  body
}
