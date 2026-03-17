#!/bin/bash
# Find which reservation platform each restaurant uses

RESTAURANTS=(
    "https://www.40lovegroup.com/"
    "https://www.mapleandash.com/scottsdale"
    "https://www.noburestaurants.com/scottsdale/"
    "https://www.catchrestaurants.com/location/catch-scottsdale/"
    "https://www.flintbybaltaire.com/dinner-menu"
    "https://www.bourbonandbones.com/"
    "https://www.mowryandcotton.com/"
    "https://shivsupperclub.com/"
    "https://www.jingscottsdale.com/"
    "https://societyswan.com/locations/scottsdale/"
    "https://www.thesexyroman.com/"
    "https://www.cleaverman.com/"
    "https://www.dimaggiosphx.com/"
    "https://www.akamaruscottsdale.com/locations"
    "https://hainoonaz.com/home"
    "https://www.chicomalo.com/"
    "https://www.kidsisterphx.com/"
    "https://www.cocinachiwas.com/"
    "https://www.confluencerestaurant.com/"
)

NAMES=(
    "40 Love"
    "Maple & Ash"
    "Nobu"
    "Catch"
    "FLINT by Baltaire"
    "Bourbon & Bones"
    "Mowry and Cotton"
    "Shiv Supper Club"
    "Jing"
    "Society Swan"
    "Sexy Roman"
    "Cleaverman"
    "DiMaggios"
    "Akamura"
    "Hainoo"
    "Chico Malo"
    "Kid Sister"
    "Cocina Chiwas"
    "Confluence"
)

for i in "${!RESTAURANTS[@]}"; do
    url="${RESTAURANTS[$i]}"
    name="${NAMES[$i]}"
    html=$(curl -sL -A "Mozilla/5.0" "$url" 2>/dev/null)
    
    platform="UNKNOWN"
    rez_url=""
    
    if echo "$html" | grep -qi "opentable"; then
        platform="OPENTABLE"
        rez_url=$(echo "$html" | grep -oE 'https://www\.opentable\.com/[^"'"'"' ]+' | head -1)
    fi
    if echo "$html" | grep -qi "resy\.com"; then
        platform="${platform}+RESY"
        rez_url=$(echo "$html" | grep -oE 'https://resy\.com/[^"'"'"' ]+' | head -1)
    fi
    if echo "$html" | grep -qi "exploretock\.com\|tock\.com"; then
        platform="${platform}+TOCK"
        rez_url=$(echo "$html" | grep -oE 'https://www\.exploretock\.com/[^"'"'"' ]+' | head -1)
    fi
    if echo "$html" | grep -qi "yelp.*reservation\|yelpreservations"; then
        platform="${platform}+YELP"
    fi
    if echo "$html" | grep -qi "sevenrooms"; then
        platform="${platform}+SEVENROOMS"
        rez_url=$(echo "$html" | grep -oE 'https://www\.sevenrooms\.com/[^"'"'"' ]+' | head -1)
    fi
    
    echo "$name | $platform | $rez_url"
done
