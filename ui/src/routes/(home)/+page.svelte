<script>
	import { onMount, onDestroy } from 'svelte'

	import { updateState, api } from '$lib/api'
  import Logo from '$lib/Logo.svelte'
	import Card from '$lib/Card.svelte'
	import PierList from '$lib/PierList.svelte'
	import BootButtons from '$lib/BootButtons.svelte'

	// load data into store
	export let data
	updateState(data)

	// init
	let inView = false

	// updateState loop
  const update = () => {
    if (inView) {
			fetch($api + '/urbits')
			.then(raw => raw.json())
    	.then(res => updateState(res))
			.catch(err => console.log(err))

			setTimeout(update, 3000)
	}}

	// Start the update loop
	onMount(()=> {
		inView = true
		update()
	})

	// end the update loop
	onDestroy(()=> inView = false)

</script>

{#if inView}
  <Card width="520px" padding={false} home={true}>
		<div style="margin: 20px 0 0 20px;">
  		<Logo />
		</div>
		<PierList />
		<BootButtons />
	</Card>
{/if}
