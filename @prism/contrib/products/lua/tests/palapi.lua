-----------------------------
-- USE AND CREATE PALETTES --
-----------------------------

------
-- prototype::
--     palette : a palette (an array of arrays of float RGB
--               colors).
--     options : a dictionary like array (see a full example
--               of use after).
--
--     :return: the expected palette (an array of arrays of
--              float RGB colors).
--
--
-- Let's consider the following use case.
--
-- lua::
--     mypal = palCreateFromPal(
--       palGistHeat,
--       {
--         extract = {2, 5, 8, 9},
--         shift   = 3,
--         reverse = true
--       }
--     )
--
-- To simplify the explanations, we will refer to the colors
-- in the ''palGistHeat'' palette as ''coul_1'', ''coul_2'',
-- etc. The options are then processed in the following order.
--
--     1) First,the extraction is done: ''mypal = {coul_2,
--     coul_5, coul_8, coul_9}''.
--
--     2) Then, the shift is applied to the extracted palette,
--     colors moving to the right if ''shift'' is positive:
--     ''mypal = {coul_5, coul_8, coul_9, coul_2}''.
--
--     3) Lastly, inversion is applied.
--
-- Finally, we obtain the following palette.
--
-- lua::
--     mypal = {coul_2, coul_9, coul_8, coul_5}
------
function palCreateFromPal(palette, options)
-- Let's build a copy.
    local result = {}

    for i, color in ipairs(palette) do
        result[i] = {color[1], color[2], color[3]}
    end

-- No option used.
    if options == nil then
        return result
    end

-- Extraction.
    if options.extract ~= nil then
        local extracted = {}

        for _ , index in ipairs(options.extract) do
            if result[index] ~= nil then
                table.insert(extracted, result[index])
            end
        end

        result = extracted
    end

-- Shifting.
    if options.shift ~= nil and options.shift ~= 0 then
        local shifted  = {}
        local pal_size = #result

        local shift = options.shift % pal_size

        for i = 1, pal_size do
            local new_i    = ((i - 1 + shift) % pal_size) + 1
            shifted[new_i] = result[i]
        end

        result = shifted
    end

-- Reversing.
    if options.reverse == true then
        local reversed = {}

        for i = #result, 1, -1 do
            table.insert(reversed, result[i])
        end

        result = reversed
    end

    return result
end
