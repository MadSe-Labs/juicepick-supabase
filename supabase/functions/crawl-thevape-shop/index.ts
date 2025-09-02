import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';
import { DOMParser } from 'https://deno.land/x/deno_dom/deno-dom-wasm.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';
const supabase = createClient(Deno.env.get('SUPABASE_URL') ?? '', Deno.env.get('SUPABASE_ANON_KEY') ?? '');
// Function to process a single product
async function processProduct(el, shopName, shopUrl) {
  const name = el.querySelector('div.add_thumb img')?.getAttribute('alt');
  const priceString = el.getAttribute('data-price');
  const price = priceString ? parseInt(priceString.replace(/[^0-9]/g, ''), 10) : null;
  const imageUrl = el.querySelector('div.add_thumb img')?.getAttribute('src');
  if (name && price) {
    let brand = 'Unknown';
    const brandMatch = name.match(/^\\\[(.*?)\\\]/); // Corrected: \\ to \ for literal backslash in regex
    if (brandMatch && brandMatch[1]) {
      brand = brandMatch[1];
    }
    // Step 1: Upsert product
    const { data: productData, error: productError } = await supabase.from('liquid_product').upsert({
      name: name,
      image_url: imageUrl,
      brand: brand
    }, {
      onConflict: 'name'
    }).select('id').single();
    if (productError) throw productError;
    if (!productData) return null;
    const productId = productData.id;
    // Step 2: Upsert price (manual SELECT + INSERT/UPDATE)
    const { data: existingPrice, error: selectError } = await supabase.from('product_price').select('id').eq('product_id', productId).eq('shop_name', shopName).single();
    if (selectError && selectError.code !== 'PGRST116') throw selectError;
    if (existingPrice) {
      const { error: updateError } = await supabase.from('product_price').update({
        price: price,
        shop_url: shopUrl
      }).eq('id', existingPrice.id);
      if (updateError) throw updateError;
    } else {
      const { error: insertError } = await supabase.from('product_price').insert({
        product_id: productId,
        shop_name: shopName,
        price: price,
        shop_url: shopUrl
      });
      if (insertError) throw insertError;
    }
    return {
      name,
      price,
      image_url: imageUrl
    };
  }
  return null;
}
async function fetchAndProcessPage(category, page, shopName, shopUrl) {
  const url = `https://xn--9k3b21rv1k.com/product/list.html?cate_no=${category}&page=${page}`;
  const response = await fetch(url);
  if (!response.ok) return []; // Ignore failed requests (like 404s)
  const html = await response.text();
  const doc = new DOMParser().parseFromString(html, 'text/html');
  if (!doc) return [];
  const productElements = doc.querySelectorAll('li.item');
  if (productElements.length === 0) return [];
  const uniqueProductsOnPage = new Map();
  for (const el of productElements){
    const name = el.querySelector('div.add_thumb img')?.getAttribute('alt');
    if (name && !uniqueProductsOnPage.has(name)) {
      uniqueProductsOnPage.set(name, el);
    }
  }
  const promises = Array.from(uniqueProductsOnPage.values()).map((el)=>processProduct(el, shopName, shopUrl));
  return (await Promise.all(promises)).filter((p)=>p !== null);
}
serve(async (req)=>{
  try {
    const categories = [
      43,
      60
    ];
    const shopName = '더베이프샵';
    const shopUrl = 'https://xn--9k3b21rv1k.com/';
    const maxPagesToTry = 10; // Let's try up to 10 pages per category
    const allPagePromises = [];
    for (const category of categories){
      for(let page = 1; page <= maxPagesToTry; page++){
        allPagePromises.push(fetchAndProcessPage(category, page, shopName, shopUrl));
      }
    }
    const resultsFromAllPages = await Promise.all(allPagePromises);
    const allProducts = resultsFromAllPages.flat();
    return new Response(JSON.stringify({
      products: allProducts,
      count: allProducts.length
    }), {
      headers: {
        'Content-Type': 'application/json'
      }
    });
  } catch (error) {
    return new Response(JSON.stringify({
      error: error.message
    }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }
});
