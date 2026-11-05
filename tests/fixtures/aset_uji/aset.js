// Contoh aset per video untuk test: latar, tokoh non-manusia (gambar sendiri), props. Gaya dari GAYA (palet terkunci).
export default (GAYA) => {
  const {C, ST, G, sorot} = GAYA;
  return {
    aksen: [],
    latar: {
      sumur_tua: t => `<rect x="-200" y="0" width="1120" height="${G}" fill="${C.s1}"/>${[0, 1, 2, 3, 4, 5, 6].map(i => `<path d="M-200,${200 + i * 120} L920,${200 + i * 120}" ${ST(3, C.s4)}/>`).join('')}${sorot(360, 0, 420, .4)}<rect x="-200" y="${G}" width="1120" height="400" fill="${C.s2}"/>`,
    },
    peran: {
      tikus: {tinggi: 70, gambar: o => `<g transform="translate(${o.x} ${o.y}) scale(${o.s})"><ellipse cx="0" cy="-26" rx="44" ry="26" fill="${C.kepala}" ${ST(4)}/><circle cx="38" cy="-40" r="18" fill="${C.kepala}" ${ST(4)}/><circle cx="44" cy="-44" r="3" fill="${C.tinta}"/><path d="M-44,-24 q-40,${-10 + 8 * Math.sin(o.t * 6)} -70,6" ${ST(4)} fill="none"/></g>`},
    },
    props: {
      keju: () => `<path d="M-40,20 L40,20 L40,-10 L-40,20 Z" fill="${C.cahaya}" ${ST(4)}/>`,
    },
    letak: {keju: 'meja'},
  };
};
