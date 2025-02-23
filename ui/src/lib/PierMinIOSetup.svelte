<script>
  import { afterUpdate } from 'svelte'
  import Fa from 'svelte-fa'
  import { faTriangleExclamation } from '@fortawesome/free-solid-svg-icons'
  import { faCircleQuestion } from '@fortawesome/free-regular-svg-icons'

  import { api } from '$lib/api'

  import EyeButton from '$lib/EyeButton.svelte'
  import PrimaryButton from '$lib/PrimaryButton.svelte'

  export let name, minIOReg

  let textToggle = 'none',
    minIOPassword = '', confirmPassword = '',
    pwdView = false, cfmView = false,
    buttonStatus = 'failure', submitted = false, showButton = true


  // Handle info and disclaimer visibility
  const handleTextToggle = val => {
    if (val == textToggle) {
      textToggle = 'none'
    } else { textToggle = val }
  }

  // Toggle first password prompt
  const togglePwdView = () => {
    pwdView = !pwdView
    document.querySelector('#minio-password').type = pwdView ? 'text' : 'password'
  }

  // Toggle confirm password prompt
  const toggleCfmView = () => {
    cfmView = !cfmView
    document.querySelector('#minio-password-1').type = cfmView ? 'text' : 'password'
  }

  // Submit MinIO password
  const submitPassword = () => {
    submitted = true
    buttonStatus = 'loading'

    fetch($api + '/urbit?urbit_id=' + name, {
			method: 'POST',
			headers: {'Content-Type': 'application/json'},
			body: JSON.stringify({'app':'minio','password':confirmPassword})
	  })
      .then(r => r.json())
      .then(d => { 
        if (d == 200) {buttonStatus = 'success'}
        else {buttonStatus = 'failure'}
        setTimeout(()=> {
          buttonStatus = 'standard', 10000
          showButton = false
        })
    })}

  afterUpdate(() => {
    if (minIOPassword.length < 8) {
      confirmPassword = ''
    }
  })

</script>

<!-- Request for minIO password if not registered -->
{#if !minIOReg}
  <div class="pier-info">

    <div class="pier-title">
      <!-- Password prompt title -->
      <span>Setup MinIO Password</span>

      <!-- Info button -->
      <button class="question-mark" on:click={()=>handleTextToggle('info')} >
        <Fa icon={faCircleQuestion} size="1.2x" />
      </button>

      <!-- MinIO disclaimer button -->
      <button class="alert-mark" on:click={()=>handleTextToggle('alert')} >
        <Fa icon={faTriangleExclamation} size="1.2x" />
      </button>
    </div>

    <!-- Info text -->
    {#if textToggle == 'info' }
      <div class="minio-info">
         Store and share files on Urbit with MinIO. All data is stored locally on your device.
      </div>
    {/if}

    <!-- MinIO disclaimer text -->
    {#if textToggle == 'alert' }
      <div class="minio-info s3-alert">Warning: if you switch between anchors, it will break your previous S3 links.</div>
    {/if}
          
    <!-- MinIO password length warning -->
    {#if (minIOPassword.length > 0) && (minIOPassword.length < 8)}
      <div class="title-smaller">Password must have at least 8 characters</div>
    {/if}

    <!-- Password input -->
    <div class="pier-cred-wrapper">
      <input
        id="minio-password"
        bind:value={minIOPassword}
        class="minio-password"
        type="password"
        placeholder="Create a password to use MinIO" />
			<EyeButton on:click={togglePwdView} view={pwdView} />
    </div>

  </div>
{/if}

<!-- Confirm Password -->
{#if (minIOPassword.length > 7) && !minIOReg}
  <div class="info">
    <div class="title-smaller">Confirm Password</div>
    <div class="pier-cred-wrapper">
      <input
        id="minio-password-1"
        bind:value={confirmPassword}
        class="minio-password"
        type="password"
        placeholder="Enter the password again" />
			<EyeButton on:click={toggleCfmView} view={cfmView} />
    </div>
  </div>
{/if}

<!-- Password Submit Button -->
{#if (confirmPassword.length > 0) && showButton}
  <PrimaryButton
    on:click={submitPassword}
    top={24}
    bottom={24}
    standard="Create MinIO"
    success="Setup complete! Toggle Remote Access to view your MinIO Console!"
    failure={submitted ? "An error occured, refresh the page and try again" : "Passwords do not match"}
    loading="Setting up MinIO for you..."
    status={!submitted && (minIOPassword == confirmPassword) ? 'standard' : buttonStatus}
  />
{/if}

<style>
  .s3-alert {
    color: orange;
  }
  .title-smaller {
    font-weight: 70;
    margin-bottom: 6px;
    text-align: left;
    font-size: 12px;
  }
  .minio-password {
    font-size: 12px;
    padding: 8px;
    background: #ffffff4d;
    border-radius: 6px;
    flex: 1;
    border: none;
    font-family: inherit;
    color: inherit;
  }
  ::placeholder {
    color: inherit;
    opacity: .6;
  }
  .minio-password:focus {
    outline: none;
  }
  .question-mark {
    color: inherit;
    cursor: pointer;
  }
  .alert-mark {
    color: orange;
    cursor: pointer;
  }
  .minio-info {
    font-size: 12px;
    margin-bottom: 12px;
    padding-right: 30px;
  }
</style>
