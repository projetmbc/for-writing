------
-- This Lua script generates a smooth color gradient using LÖVE
-- (aka Love2D).
--
-- How to use this script?
--
--     1. Install LÖVE from https://love2d.org
--
--     2. Running the folder with LÖVE, you should see a window
--        displaying a horizontal color spectrum.
--
--         * On Windows: drag and drop the folder onto love.exe
--
--         * On macOS/Linux: in the terminal, run the command
--           term::''open -n -a love path/to/the/folder/of/this/file''.
------

-- Accent from Matplotlib
PALETTE = {
  {0.49803, 0.78823, 0.49803},
  {0.49803, 0.78823, 0.49803},
  {0.74509, 0.68235, 0.83137},
  {0.99215, 0.75294, 0.52549},
  {1.0, 1.0, 0.6},
  {0.2196, 0.42352, 0.69019},
  {0.94117, 0.00784, 0.49803},
  {0.74901, 0.35686, 0.09019},
  {0.4, 0.4, 0.4},
  {0.4, 0.4, 0.4}
}



function love.load()
  local largeur, hauteur = 800, 200

  local image = love.image.newImageData(largeur, hauteur)

  local function linear_interpol(a, b, t)
    return a + (b - a) * t
  end

  for x = 0, largeur - 1 do
    local pos = x / (largeur - 1) * (#PALETTE - 1)
    local i = math.floor(pos) + 1
    local t = pos - (i - 1)

    local c1, c2 = PALETTE[i], PALETTE[math.min(i+1, #PALETTE)]

    local r = linear_interpol(c1[1], c2[1], t)
    local g = linear_interpol(c1[2], c2[2], t)
    local b = linear_interpol(c1[3], c2[3], t)

    for y = 0, hauteur - 1 do
      image:setPixel(x, y, r, g, b, 1)
    end
  end

  spectrum = love.graphics.newImage(image)
end

function love.draw()
  love.graphics.draw(spectrum, 0, 0)
end
