---------------------------------
-- NO TRANSLATION NEEDED HERE! --
---------------------------------

function drawpals(names)
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
