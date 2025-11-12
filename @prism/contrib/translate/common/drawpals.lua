---------------------------------
-- NO TRANSLATION NEEDED HERE! --
---------------------------------

function drawSimPals(names)
  for _ , palname in ipairs(names) do
    local g = graph:new{
      window = {-5, 15, -5, 5},
      bbox   = false,
      border = false
    }

    g:Linewidth(1)

    local A     = Z(-5, 4)
    local h, dh = Z(0, -1), Z(0, -1.1)
    local L, N  = 12.5, 150
    local dl    = L / N

    local pal = getPal(palname)

    for k = 1, N do
      local color = palette(pal, (k - 1) / (N - 1))

      g:Drectangle(
        A, A + h, A + h + dl,
           "color = " .. color
        .. ", fill = " .. color
      )

      A = A+dl
    end

    g:Drectangle(A, A + h, A + h - L)

    g:Dlabel(
      "\\quad\\large\\texttt{\\bfseries " .. palname .. "}",
      A + h / 2,
      {pos = "E"}
    )

    g:Sendtotex()

    tex.sprint("\\smallskip\\par")
  end
end


function drawSpectrum(pal)
  local g = graph:new{
    window = {-5, 5, -5, 5},
    bbox   = false,
    border = false
  }

  g:Linewidth(1)

  local A, h, dh = Z(-5, 4), Z(0, -1), Z(0, -.75)
  local L, N = 5, 150
  local dl = L / N

  for k = 1, N do
    local color = palette(pal, (k - 1) / (N - 1))

    g:Drectangle(
      A, A+h, A+h+dl,
      "color = " .. color .. ", fill = " .. color
    )

    A = A+dl
  end

  g:Drectangle(A, A+h, A+h-L)

  g:Sendtotex()
end

function drawPalette(pal)
  local palsize  = #pal
  local paldim   = .5
  local paldelta = .2

  local g = graph:new{
    window = {-100, 100, -5, 5},
    bbox   = false
  }

  g:Linewidth(2)

  local A = Z(-20, 4)
  local v = Z(0, -paldim)

  for k = 1, palsize do
    local color = rgb(pal[k])

    g:Drectangle(
      A, A + paldim, A + paldim + v,
      "color = black, fill = " .. color
    )

    A = A + paldim + paldelta
  end

  g:Sendtotex()
end

function drawCategoPals(names)
  table.sort(names)

  tex.print("\\begin{longtable}[c]{>{\\centering\\arraybackslash}m{5cm}>{\\centering\\arraybackslash}m{2.25cm}>{\\centering\\arraybackslash}m{8cm}}")
--  tex.print("\\rule[-2ex]{0pt}{3ex}\\textbf{Spectrum} & \\rule[-2ex]{0pt}{3ex}\\textbf{Name} & \\rule[-2ex]{0pt}{3ex}\\textbf{Palette} \\\\ ")
--  tex.print("\\endhead")


  for _, name in ipairs(names) do
    local pal = getPal(name)

    drawSpectrum(pal)

    tex.print(" & ")
    tex.print("\\bfseries\\texttt{" .. name .. "}")
    tex.print(" & ")

    drawPalette(pal)

    tex.print(" \\\\ ")
  end

  tex.print("\\end{longtable}")
end
