local ld = luadraw

local M = ld.pt3d.M

local vecK = ld.pt3d.vecK

function drawsurf(PAL)
  local cos, sin = math.cos, math.sin, math.pi

  local g = ld.graph3d:new{
    window3d = {0, 5, 0, 10, 0, 11},
    adjust2d = true,
    size     = {12, 8.5, 0},
    bbox     = false,
    viewdir  = {220, 60},
    margin   = {0, 0, 0, 0}
  }

  g:Linewidth(2)

  local S = ld.surface(
    function(u, v)
      return M(u, v, (u + v) / (2 + cos(u)*sin(v)))
    end,
    0, 5, 0, 10,
    {30, 30}
  )

  local n = 10

  local colors = ld.getpalette(PAL, n, true)

  local niv, S1 = {}

  for k = 1, n do
    S1, S = ld.cutfacet(S, {M(0, 0, k), -vecK})

    ld.insert(
      niv,
      {
        S1,
        {
          color     = colors[k],
          mode      = ld.mShaded,
          edgewidth = 0.5
        }
      }
    )
  end

  ld.insert(
    niv,
    {
      S,
      {color = colors[n + 1]}
    }
  )

  g:Dboxaxes3d({
    grid      = true,
    gridcolor = "gray",
    fillcolor = "lightgray"
  })

  g:Dmixfacet(table.unpack(niv))

  for k = 1, n do
    g:Dballdots3d(
      M(5, 0, k),
      ld.rgb(colors[k])
    )
  end

  g:Show()
end
